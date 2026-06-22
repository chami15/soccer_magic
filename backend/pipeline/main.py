"""
Soccer Magic — Pipeline Orchestrator (SPECv2)
Coleta dados das 48 seleções via Sofascore e persiste no Supabase.
Fluxo: season discovery → teams → recent matches → window → stats/incidents → transform → persist
"""
import argparse
import logging
import sys
from datetime import date, datetime, timedelta, timezone

import httpx

import collector
import persistence
from collector import WC_TOURNAMENT_ID, get_wc_2026_season_id, get_wc_teams
from collector import get_team_recent_matches, get_match_statistics, get_match_incidents
from collector import get_tournament_next_events, get_tournament_last_events
from collector import get_team_goal_distributions, get_h2h_events
from transformer import transform, summarize_h2h
from window import build_window

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    encoding="utf-8",
)
logger = logging.getLogger("main")


def _is_home(match: dict, team_id: int) -> bool:
    return match["homeTeam"]["id"] == team_id


def _opponent_name(match: dict, team_id: int) -> str:
    if _is_home(match, team_id):
        return match["awayTeam"].get("name", "")
    return match["homeTeam"].get("name", "")


def _build_match_log_row(match: dict, team_id: int, in_window: bool) -> dict:
    tournament = match.get("tournament", {}).get("uniqueTournament", {})
    tournament_id = tournament.get("id")
    return {
        "match_id": match["id"],
        "team_id": team_id,
        "opponent_name": _opponent_name(match, team_id),
        "date": datetime.fromtimestamp(match["startTimestamp"]).date().isoformat(),
        "tournament_id": tournament_id,
        "tournament_name": tournament.get("name"),
        "match_type": "Copa" if tournament_id == WC_TOURNAMENT_ID else "Amistoso",
        "score_home": match["homeScore"].get("current"),
        "score_away": match["awayScore"].get("current"),
        "score_ht_home": match["homeScore"].get("period1"),
        "score_ht_away": match["awayScore"].get("period1"),
        "is_in_window": in_window,
        "stats_raw": None,
    }


def _build_schedule_row(match: dict, h2h_summary: dict | None) -> dict:
    tournament = match.get("tournament", {})
    return {
        "match_id": match["id"],
        "custom_id": match.get("customId"),
        "home_team_id": match["homeTeam"]["id"],
        "away_team_id": match["awayTeam"]["id"],
        "home_team_name": match["homeTeam"].get("name", ""),
        "away_team_name": match["awayTeam"].get("name", ""),
        "group_name": tournament.get("groupName"),
        "round": match.get("roundInfo", {}).get("round"),
        "match_date": datetime.fromtimestamp(match["startTimestamp"], tz=timezone.utc).date().isoformat(),
        "start_timestamp": match["startTimestamp"],
        "status_type": match.get("status", {}).get("type"),
        "venue_city": match.get("venue", {}).get("city", {}).get("name"),
        "h2h_summary": h2h_summary,
    }


def save_tournament_schedule(client: httpx.Client) -> None:
    """Salva o calendário completo (próximos + últimos jogos do torneio) para filtros no frontend.
    Para jogos ainda não realizados ('notstarted'), busca também o histórico de confrontos
    diretos (h2h), do ponto de vista do time de casa — não vale a pena buscar h2h para
    jogos já encerrados, pois o resultado dessa partida específica não muda a análise."""
    events = get_tournament_next_events(client) + get_tournament_last_events(client)
    rows = []
    for event in events:
        h2h_summary = None
        custom_id = event.get("customId")
        if event.get("status", {}).get("type") == "notstarted" and custom_id:
            try:
                h2h_events = get_h2h_events(client, custom_id)
                h2h_summary = summarize_h2h(h2h_events, event["homeTeam"]["id"])
            except Exception as exc:
                logger.warning("Erro ao buscar h2h para %s: %s", custom_id, exc)
        rows.append(_build_schedule_row(event, h2h_summary))
    try:
        persistence.save_matches_schedule(rows)
    except Exception as exc:
        logger.error("Erro ao salvar matches_schedule: %s", exc)


def filter_teams_playing_on(client: httpx.Client, teams: list[dict], target_date: str) -> tuple[list[dict], list[dict]]:
    """Filtra as seleções com jogo agendado em target_date (YYYY-MM-DD).
    Uma única chamada ao torneio em vez de uma chamada por time."""
    next_events = get_tournament_next_events(client)
    matches_on_date = [
        e for e in next_events
        if datetime.fromtimestamp(e["startTimestamp"], tz=timezone.utc).date().isoformat() == target_date
    ]

    team_ids_playing = set()
    for match in matches_on_date:
        team_ids_playing.add(match["homeTeam"]["id"])
        team_ids_playing.add(match["awayTeam"]["id"])

    playing = [t for t in teams if t["id"] in team_ids_playing]
    return playing, matches_on_date


def process_team(client: httpx.Client, team: dict, errors: list) -> tuple[bool, bool]:
    """Processa uma seleção. Retorna (success, window_changed)."""
    team_id = team["id"]
    team_name = team["name"]
    logger.info("Processando: %s (id=%s)", team_name, team_id)

    try:
        persistence.save_team(team)
    except Exception as exc:
        logger.error("Erro ao salvar time %s: %s", team_name, exc)
        errors.append({"team_id": team_id, "team_name": team_name, "error": str(exc), "phase": "save_team"})
        return False, False

    try:
        matches_raw = get_team_recent_matches(client, team_id, count=10)
    except Exception as exc:
        logger.error("Erro ao buscar partidas de %s: %s", team_name, exc)
        errors.append({"team_id": team_id, "team_name": team_name, "error": str(exc), "phase": "get_matches"})
        return False, False

    if not matches_raw:
        logger.warning("Nenhuma partida encerrada para %s", team_name)
        return True, False

    window_result = build_window(matches_raw, WC_TOURNAMENT_ID)
    logger.info(
        "%s -> janela=%d (Copa=%d, Amistoso=%d, qualidade=%s)",
        team_name, len(window_result.window),
        window_result.copa_count, window_result.friendly_count,
        window_result.data_quality,
    )

    if window_result.data_quality == "insufficient":
        logger.warning("Dados insuficientes para %s — salvando row mínima", team_name)
        try:
            persistence.save_team_stats({
                "team_id": team_id,
                "copa_count": 0,
                "friendly_count": 0,
                "data_quality": "insufficient",
            })
        except Exception as exc:
            logger.error("Erro ao salvar stats insuficientes para %s: %s", team_name, exc)
        return True, False

    # Coletar stats e incidentes para cada partida da janela
    window_match_ids = {m["id"] for m in window_result.window}
    all_match_ids = {m["id"] for m in matches_raw}

    match_stats: dict[int, list] = {}
    match_incidents: dict[int, list] = {}
    match_log_rows: list[dict] = []

    for match in window_result.window:
        mid = match["id"]
        try:
            match_stats[mid] = get_match_statistics(client, mid)
        except Exception as exc:
            logger.warning("Stats não disponíveis para match %s: %s", mid, exc)
            match_stats[mid] = []
        try:
            match_incidents[mid] = get_match_incidents(client, mid)
        except Exception as exc:
            logger.warning("Incidentes não disponíveis para match %s: %s", mid, exc)
            match_incidents[mid] = []
        match_log_rows.append(_build_match_log_row(match, team_id, True))

    try:
        persistence.save_match_log(match_log_rows)
    except Exception as exc:
        logger.error("Erro ao salvar match_log para %s: %s", team_name, exc)
        errors.append({"team_id": team_id, "team_name": team_name, "error": str(exc), "phase": "save_match_log"})

    try:
        goal_distributions = get_team_goal_distributions(client, team_id)
    except Exception as exc:
        logger.warning("Goal distributions não disponíveis para %s: %s", team_name, exc)
        goal_distributions = []

    stats_row = transform(team_id, window_result, match_stats, match_incidents, goal_distributions)

    prev_window = persistence.get_current_window(team_id)
    window_changed = prev_window != stats_row["games_window"]

    try:
        persistence.save_team_stats(stats_row)
    except Exception as exc:
        logger.error("Erro ao salvar team_stats para %s: %s", team_name, exc)
        errors.append({"team_id": team_id, "team_name": team_name, "error": str(exc), "phase": "save_team_stats"})
        return False, False

    logger.info("[OK] %s concluido (window_changed=%s)", team_name, window_changed)
    return True, window_changed


def run(limit: int | None = None, season: int = 2026, only_playing_tomorrow: bool = True):
    started_at = datetime.now(timezone.utc)
    logger.info("=== Soccer Magic Pipeline v2 iniciado em %s (season=%s) ===", started_at.isoformat(), season)

    with httpx.Client() as client:
        try:
            season_id = get_wc_2026_season_id(client)
            logger.info("Season 2026 ID: %s", season_id)
        except Exception as exc:
            logger.error("Falha ao descobrir season 2026: %s", exc)
            return

        teams = get_wc_teams(client, season_id)
        save_tournament_schedule(client)

        if only_playing_tomorrow:
            tomorrow = (date.today() + timedelta(days=1)).isoformat()
            teams, _matches_tomorrow = filter_teams_playing_on(client, teams, tomorrow)
            logger.info("Seleções com jogo em %s: %d", tomorrow, len(teams))

        if limit:
            teams = teams[:limit]
        logger.info("Seleções a processar: %d", len(teams))

        teams_processed = 0
        windows_changed = 0
        errors: list[dict] = []

        for team in teams:
            success, changed = process_team(client, team, errors)
            if success:
                teams_processed += 1
            if changed:
                windows_changed += 1

    finished_at = datetime.now(timezone.utc)

    run_record = {
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "teams_processed": teams_processed,
        "windows_changed": windows_changed,
        "errors_count": len(errors),
        "error_log": errors if errors else None,
        "triggered_by": "manual",
    }

    try:
        persistence.save_pipeline_run(run_record)
    except Exception as exc:
        logger.error("Erro ao salvar pipeline run: %s", exc)

    summary = (
        f"{teams_processed} seleções processadas | "
        f"{windows_changed} janelas alteradas | "
        f"{len(errors)} erros"
    )
    logger.info("=== Pipeline concluído: %s ===", summary)
    print(summary)
    return run_record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Soccer Magic Pipeline v2 — Sofascore")
    parser.add_argument("--limit", type=int, default=None, help="Limitar número de seleções (teste)")
    parser.add_argument("--season", type=int, default=2026, help="Ano da season (padrão: 2026)")
    parser.add_argument("--all-teams", action="store_true", help="Processar as 48 seleções, ignorando o filtro de jogo de amanhã")
    args = parser.parse_args()
    run(limit=args.limit, season=args.season, only_playing_tomorrow=not args.all_teams)

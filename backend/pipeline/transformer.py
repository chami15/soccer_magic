"""
Soccer Magic — Transformer (SPECv2)
Converte dados Sofascore da janela deslizante em linhas do team_stats.
"""
from datetime import datetime, timezone
from window import WindowResult

# Mapeamento nome Sofascore → chave interna
STATS_MAP = {
    "Ball possession":   "possession",
    "Total shots":       "shots_total",
    "Shots on target":   "shots_on_goal",
    "Blocked shots":     "blocked_shots",
    "Shots inside box":  "shots_inside_box",
    "Shots outside box": "shots_outside_box",
    "Corner kicks":      "corners",
    "Offsides":          "offsides",
    "Fouls":             "fouls",
    "Yellow cards":      "yellow_cards",
    "Red cards":         "red_cards",
    "Goalkeeper saves":  "saves",
    "Total passes":      "passes_total",
    "Accurate passes":   "passes_accurate",
    "Accurate passes %": "passes_pct",
}


def coalesce(val):
    return val if val is not None else 0


def _is_home(match: dict, team_id: int) -> bool:
    return match["homeTeam"]["id"] == team_id


def get_team_goals_scored(match: dict, team_id: int) -> int:
    if _is_home(match, team_id):
        return coalesce(match["homeScore"].get("current"))
    return coalesce(match["awayScore"].get("current"))


def get_team_goals_conceded(match: dict, team_id: int) -> int:
    if _is_home(match, team_id):
        return coalesce(match["awayScore"].get("current"))
    return coalesce(match["homeScore"].get("current"))


def get_result(match: dict, team_id: int) -> str:
    scored = get_team_goals_scored(match, team_id)
    conceded = get_team_goals_conceded(match, team_id)
    if scored > conceded:
        return "V"
    if scored == conceded:
        return "E"
    return "D"


def _extract_stats(statistics: list, is_home: bool) -> dict:
    """Extrai stats do lado correto (home/away) da resposta /statistics do Sofascore."""
    side = "home" if is_home else "away"
    result = {}
    for group in statistics:
        for item in group.get("statisticsItems", []):
            key = STATS_MAP.get(item.get("name"))
            if key:
                raw = item.get(side)
                if raw is not None:
                    val = str(raw).replace("%", "").strip()
                    try:
                        result[key] = float(val) if val else 0.0
                    except ValueError:
                        result[key] = 0.0
    return result


def _count_goals_in_period(incidents: list, team_id: int, period: int) -> int:
    """Conta gols marcados pelo time em um tempo (period=1 ou 2) via incidentes Sofascore."""
    return sum(
        1
        for inc in incidents
        if inc.get("incidentType") == "goal"
        and inc.get("period") == period
        and inc.get("team", {}).get("id") == team_id
    )


def summarize_goal_distribution(goal_distributions: list[dict]) -> dict | None:
    """Resume o /goal-distributions (agregado da temporada inteira pelo Sofascore — escopo
    diferente da janela deslizante de avg_goals_1h/2h, que é por jogo dentro da janela)."""
    overall = next((d for d in goal_distributions if d.get("type") == "overall"), None)
    if not overall:
        return None
    return {
        "season_matches": overall.get("matches"),
        "season_goals_scored": overall.get("scoredGoals"),
        "season_goals_conceded": overall.get("concededGoals"),
        "periods": overall.get("periods", []),
    }


def summarize_h2h(h2h_events: list[dict], team_id: int) -> dict | None:
    """Resume o histórico de confrontos diretos /h2h/events para o team_id informado."""
    if not h2h_events:
        return None
    wins = draws = losses = 0
    for ev in h2h_events:
        if ev.get("status", {}).get("type") != "finished":
            continue
        result = get_result(ev, team_id) if _is_home(ev, team_id) or ev["awayTeam"]["id"] == team_id else None
        if result == "V":
            wins += 1
        elif result == "E":
            draws += 1
        elif result == "D":
            losses += 1
    return {"matches": len(h2h_events), "wins": wins, "draws": draws, "losses": losses}


def transform(
    team_id: int,
    window: WindowResult,
    match_stats: dict,    # {match_id: lista de grupos /statistics}
    match_incidents: dict,  # {match_id: lista de incidentes /incidents}
) -> dict:
    """
    Transforma os dados da janela em uma linha de team_stats.
    Divisor REAL: len(window.window) — nunca fixo em 5.
    """
    n = len(window.window)

    goals_scored_list = [get_team_goals_scored(m, team_id) for m in window.window]
    goals_conceded_list = [get_team_goals_conceded(m, team_id) for m in window.window]

    total_scored = sum(goals_scored_list)
    total_conceded = sum(goals_conceded_list)

    over15_count = sum(
        1 for m in window.window
        if coalesce(m["homeScore"].get("current")) + coalesce(m["awayScore"].get("current")) >= 2
    )
    over25_count = sum(
        1 for m in window.window
        if coalesce(m["homeScore"].get("current")) + coalesce(m["awayScore"].get("current")) >= 3
    )
    over35_count = sum(
        1 for m in window.window
        if coalesce(m["homeScore"].get("current")) + coalesce(m["awayScore"].get("current")) >= 4
    )
    btts_count = sum(
        1 for m in window.window
        if coalesce(m["homeScore"].get("current")) > 0
        and coalesce(m["awayScore"].get("current")) > 0
    )
    clean_sheets = sum(1 for g in goals_conceded_list if g == 0)

    # Acumular stats por partida
    stats_acc: dict[str, list] = {k: [] for k in STATS_MAP.values()}
    corners_list: list = []

    for match in window.window:
        mid = match["id"]
        is_home = _is_home(match, team_id)
        s = _extract_stats(match_stats.get(mid, []), is_home)
        for k in STATS_MAP.values():
            stats_acc[k].append(coalesce(s.get(k)))
        corners_list.append(coalesce(s.get("corners")))

    over35_corners_count = sum(1 for c in corners_list if c >= 4)

    # Gols por tempo via incidentes
    goals_1h = [
        _count_goals_in_period(match_incidents.get(m["id"], []), team_id, 1)
        for m in window.window
    ]
    goals_2h = [
        _count_goals_in_period(match_incidents.get(m["id"], []), team_id, 2)
        for m in window.window
    ]

    form_sequence = " ".join(get_result(m, team_id) for m in window.window)

    avg_3 = sum(goals_scored_list[:3]) / 3 if n >= 3 else None
    avg_5 = total_scored / n
    trend_goals_3v5 = round(avg_3 - avg_5, 2) if avg_3 is not None else None

    def avg(lst: list):
        return round(sum(lst) / n, 2) if lst else None

    return {
        "team_id": team_id,
        "copa_count": window.copa_count,
        "friendly_count": window.friendly_count,
        "data_quality": window.data_quality,
        "games_window": [m["id"] for m in window.window],
        "avg_goals_scored": round(avg_5, 2),
        "avg_goals_conceded": round(total_conceded / n, 2),
        "avg_shots_total": avg(stats_acc["shots_total"]),
        "avg_shots_on_goal": avg(stats_acc["shots_on_goal"]),
        "avg_shots_inside_box": avg(stats_acc["shots_inside_box"]),
        "avg_shots_outside_box": avg(stats_acc["shots_outside_box"]),
        "avg_blocked_shots": avg(stats_acc["blocked_shots"]),
        "avg_corners": avg(stats_acc["corners"]),
        "avg_possession": avg(stats_acc["possession"]),
        "avg_passes_total": avg(stats_acc["passes_total"]),
        "avg_passes_accurate": avg(stats_acc["passes_accurate"]),
        "avg_passes_pct": avg(stats_acc["passes_pct"]),
        "avg_offsides": avg(stats_acc["offsides"]),
        "avg_fouls": avg(stats_acc["fouls"]),
        "avg_yellow_cards": avg(stats_acc["yellow_cards"]),
        "avg_red_cards": avg(stats_acc["red_cards"]),
        "avg_saves": avg(stats_acc["saves"]),
        "clean_sheets": clean_sheets,
        "over15_pct": round(over15_count / n * 100, 1),
        "over25_pct": round(over25_count / n * 100, 1),
        "over35_pct": round(over35_count / n * 100, 1),
        "btts_pct": round(btts_count / n * 100, 1),
        "over35_corners_pct": round(over35_corners_count / n * 100, 1),
        "avg_goals_1h": avg(goals_1h),
        "avg_goals_2h": avg(goals_2h),
        "form_sequence": form_sequence,
        "trend_goals_3v5": trend_goals_3v5,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

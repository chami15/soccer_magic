"""
Transformer — fato_partida
Converte 1 evento de partida do Sofascore (collector.get_team_recent_matches
ou equivalente) na linha esperada por persisters/partida.py.
"""

from datetime import datetime, timezone

WC_TOURNAMENT_ID = 16


def transform_partida(match: dict) -> dict:
    home_id = match["homeTeam"]["id"]
    away_id = match["awayTeam"]["id"]
    placar_home = match["homeScore"].get("current")
    placar_away = match["awayScore"].get("current")
    status = match.get("status", {}).get("type")

    vencedor_id = None
    if status == "finished" and placar_home is not None and placar_away is not None:
        if placar_home > placar_away:
            vencedor_id = home_id
        elif placar_away > placar_home:
            vencedor_id = away_id

    tournament = match.get("tournament", {})
    tournament_id = tournament.get("uniqueTournament", {}).get("id")

    return {
        "id": match["id"],
        "custom_id": match.get("customId"),
        "selecao_home_id": home_id,
        "selecao_away_id": away_id,
        "placar_home": placar_home,
        "placar_away": placar_away,
        "placar_ht_home": match["homeScore"].get("period1"),
        "placar_ht_away": match["awayScore"].get("period1"),
        "status": status,
        "vencedor_id": vencedor_id,
        "tipo": "Copa" if tournament_id == WC_TOURNAMENT_ID else "Amistoso",
        "grupo": tournament.get("groupName"),
        "rodada": match.get("roundInfo", {}).get("round"),
        "data_partida": datetime.fromtimestamp(match["startTimestamp"], tz=timezone.utc).date().isoformat(),
        "cidade": match.get("venue", {}).get("city", {}).get("name"),
    }

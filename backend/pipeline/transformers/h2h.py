"""
Transformer — fato_h2h_evento
Converte 1 evento de collector.get_h2h_events() na linha esperada por
persisters/h2h.py.

selecao_a_id e o time "ancora" (o time que estamos consultando); selecao_b_id
e o adversario, identificado dinamicamente pois em eventos historicos o
mando de campo (home/away) pode variar de confronto pra confronto.

performance_a/performance_b ficam None por enquanto — o endpoint de h2h nao
retorna nota de desempenho separada (mesma situacao do performance_rating
em estatistica.py).
"""

from datetime import datetime, timezone


def transform_h2h(event: dict, selecao_a_id: int) -> dict:
    home = event["homeTeam"]
    away = event["awayTeam"]
    home_score = event.get("homeScore", {}).get("current")
    away_score = event.get("awayScore", {}).get("current")

    if home["id"] == selecao_a_id:
        selecao_b_id = away["id"]
        placar_a, placar_b = home_score, away_score
    else:
        selecao_b_id = home["id"]
        placar_a, placar_b = away_score, home_score

    vencedor_id = None
    winner_code = event.get("winnerCode")
    if winner_code == 1:
        vencedor_id = home["id"]
    elif winner_code == 2:
        vencedor_id = away["id"]

    tournament = event.get("tournament", {})
    torneio_nome = tournament.get("name") or tournament.get("uniqueTournament", {}).get("name")

    data_partida = None
    if event.get("startTimestamp"):
        data_partida = datetime.fromtimestamp(event["startTimestamp"], tz=timezone.utc).date().isoformat()

    return {
        "id": event["id"],
        "selecao_a_id": selecao_a_id,
        "selecao_b_id": selecao_b_id,
        "placar_a": placar_a,
        "placar_b": placar_b,
        "vencedor_id": vencedor_id,
        "torneio_nome": torneio_nome,
        "data_partida": data_partida,
        "performance_a": None,
        "performance_b": None,
    }


def extrair_adversarios(events: list[dict], selecao_a_id: int) -> list[dict]:
    """Retorna os objetos 'team' dos adversarios unicos (sem duplicar por id) —
    usado para upsertar em dim_selecao antes de inserir os eventos h2h (FK)."""
    vistos: dict[int, dict] = {}
    for event in events:
        home = event["homeTeam"]
        away = event["awayTeam"]
        adversario = away if home["id"] == selecao_a_id else home
        if adversario["id"] not in vistos:
            vistos[adversario["id"]] = adversario
    return list(vistos.values())

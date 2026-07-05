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

from datetime import datetime, timedelta, timezone

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _score(score_dict: dict | None) -> int | None:
    """Extrai placar tentando current → display → period1+period2 (eventos antigos do Sofascore)."""
    if not score_dict:
        return None
    if score_dict.get("current") is not None:
        return score_dict["current"]
    if score_dict.get("display") is not None:
        try:
            return int(score_dict["display"])
        except (ValueError, TypeError):
            pass
    # Fallback: soma dos períodos
    p1 = score_dict.get("period1") or 0
    p2 = score_dict.get("period2") or 0
    et = score_dict.get("overtime") or 0
    pen = score_dict.get("penalties") or 0
    total = p1 + p2 + et + pen
    return total if total > 0 else None


def transform_h2h(event: dict, selecao_a_id: int) -> dict:
    home = event["homeTeam"]
    away = event["awayTeam"]
    home_score = _score(event.get("homeScore"))
    away_score = _score(event.get("awayScore"))

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
        # timedelta a partir do epoch em vez de datetime.fromtimestamp: a libc do
        # Windows rejeita (OSError 22) timestamps anteriores a 1970, e o H2H traz
        # confrontos historicos antigos que caem nesse caso.
        data_partida = (_EPOCH + timedelta(seconds=event["startTimestamp"])).date().isoformat()

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

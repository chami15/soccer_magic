"""
Transformer — fato_evento_partida (+ extracao dos jogadores para dim_jogador)
Converte os incidentes de collector.get_match_incidents() em linhas de
fato_evento_partida. So tratamos os 3 tipos citados no schema: gol, cartao
(amarelo/vermelho) e substituicao — outros incidentTypes (ex: 'period',
'injuryTime', 'varDecision') sao ignorados por ora.

ATENCAO: o formato exato dos campos de incidente (nomes de chave como
'incidentType'/'incidentClass'/'isHome', presenca de 'id' em substituicoes)
ainda nao foi validado contra um payload real do Sofascore — assim como
aconteceu com fato_estatistica_selecao_partida, e esperado que algum nome
de campo precise de ajuste apos o primeiro teste real.

var_decisao fica None por enquanto (deprioritizado, mesma situacao do
performance_rating em estatistica.py) — nao temos confirmacao de como o
Sofascore marca uma decisao de VAR dentro do proprio incidente de gol/cartao.
"""

TIPO_CARTAO = {
    "yellow": "cartao_amarelo",
    "red": "cartao_vermelho",
    "yellowRed": "cartao_vermelho",
}


def _selecao_id(incident: dict, match: dict) -> int:
    is_home = incident.get("isHome", True)
    return match["homeTeam"]["id"] if is_home else match["awayTeam"]["id"]


def extrair_jogadores(incidents: list[dict], match: dict) -> list[tuple[dict, int]]:
    """Retorna [(player_dict, selecao_id), ...] sem duplicar por id de jogador —
    usado para popular dim_jogador antes de inserir os eventos (FK)."""
    vistos: dict[int, tuple[dict, int]] = {}
    for incident in incidents:
        selecao_id = _selecao_id(incident, match)
        candidatos = []
        if incident.get("player"):
            candidatos.append(incident["player"])
        if incident.get("assist1"):
            candidatos.append(incident["assist1"])
        if incident.get("playerIn"):
            candidatos.append(incident["playerIn"])
        if incident.get("playerOut"):
            candidatos.append(incident["playerOut"])
        for player in candidatos:
            pid = player.get("id")
            if pid and pid not in vistos:
                vistos[pid] = (player, selecao_id)
    return list(vistos.values())


def transform_eventos(incidents: list[dict], match: dict) -> list[dict]:
    rows = []
    for incident in incidents:
        tipo_incidente = incident.get("incidentType")
        incident_id = incident.get("id")
        if incident_id is None:
            continue

        selecao_id = _selecao_id(incident, match)
        base = {
            "id": incident_id,
            "partida_id": match["id"],
            "selecao_id": selecao_id,
            "minuto": incident.get("time"),
            "minuto_extra": incident.get("addedTime"),
            "jogador_id": None,
            "assistencia_jogador_id": None,
            "jogador_saida_id": None,
            "jogador_entrada_id": None,
            "tipo_gol": None,
            "var_decisao": None,
        }

        if tipo_incidente == "goal":
            base["tipo_evento"] = "gol"
            base["jogador_id"] = incident.get("player", {}).get("id")
            base["assistencia_jogador_id"] = incident.get("assist1", {}).get("id") if incident.get("assist1") else None
            base["tipo_gol"] = incident.get("incidentClass")
            rows.append(base)

        elif tipo_incidente == "card":
            tipo_evento = TIPO_CARTAO.get(incident.get("incidentClass"))
            if tipo_evento is None:
                continue
            base["tipo_evento"] = tipo_evento
            base["jogador_id"] = incident.get("player", {}).get("id")
            rows.append(base)

        elif tipo_incidente == "substitution":
            base["tipo_evento"] = "substituicao"
            base["jogador_saida_id"] = incident.get("playerOut", {}).get("id")
            base["jogador_entrada_id"] = incident.get("playerIn", {}).get("id")
            rows.append(base)

    return rows

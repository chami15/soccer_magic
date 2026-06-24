"""
Transformer — fato_estatistica_selecao_partida
Converte os 'groups' retornados por collector.get_match_statistics() (que vem
junto home/away num unico payload) em 2 linhas (selecao + adversaria) para a
tabela fato_estatistica_selecao_partida.

A API do Sofascore organiza as estatisticas em grupos (ex: "Match overview",
"Shots", "Passes"...) e cada item dentro de statisticsItems tem um 'key'
estavel (ex: 'ballPossession', 'totalShotsOnGoal') com valores numericos em
homeValue/awayValue — por isso a primeira coisa que fazemos e achatar tudo
num dict {key: {"home":..., "away":...}}, independente do agrupamento.
"""

import re


def _flatten_por_key(groups: list[dict]) -> dict[str, dict]:
    flat: dict[str, dict] = {}
    for group in groups:
        for item in group.get("statisticsItems", []):
            key = item.get("key")
            if not key:
                continue
            flat[key] = item
    return flat


def _num(item: dict | None, lado: str) -> float | None:
    if item is None:
        return None
    value = item.get(f"{lado}Value")
    if value is not None:
        return value
    bruto = item.get(lado)
    if bruto is None:
        return None
    match = re.search(r"[\d.]+", str(bruto))
    return float(match.group()) if match else None


def _linha_para_lado(
    flat: dict[str, dict],
    lado: str,
    partida_id: int,
    selecao_id: int,
    gols_marcados: int | None,
    gols_sofridos: int | None,
    resultado: str | None,
    gols_1_tempo: int | None,
    gols_2_tempo: int | None,
    performance_rating: float | None,
) -> dict:
    return {
        "partida_id": partida_id,
        "selecao_id": selecao_id,
        "resultado": resultado,
        "gols_marcados": gols_marcados,
        "gols_sofridos": gols_sofridos,
        "posse_bola": _num(flat.get("ballPossession"), lado),
        "chutes_total": _num(flat.get("totalShotsOnGoal"), lado),
        "chutes_no_gol": _num(flat.get("shotsOnGoal"), lado),
        "chutes_bloqueados": _num(flat.get("blockedScoringAttempt"), lado),
        "chutes_dentro_area": _num(flat.get("shotsInsideBox"), lado),
        "chutes_fora_area": _num(flat.get("shotsOutsideBox"), lado),
        "escanteios": _num(flat.get("cornerKicks"), lado),
        "impedimentos": _num(flat.get("offsides"), lado),
        "faltas": _num(flat.get("fouls"), lado),
        "cartoes_amarelos": _num(flat.get("yellowCards"), lado),
        "cartoes_vermelhos": _num(flat.get("redCards"), lado),
        "defesas": _num(flat.get("goalkeeperSaves"), lado),
        "passes_total": _num(flat.get("totalPasses"), lado),
        "passes_certos": _num(flat.get("accuratePasses"), lado),
        "passes_precisao_pct": _num(flat.get("passAccuracy"), lado),
        "gols_1_tempo": gols_1_tempo,
        "gols_2_tempo": gols_2_tempo,
        "performance_rating": performance_rating,
    }


def transform_estatistica(
    groups: list[dict],
    match: dict,
    performance_points: dict[int, float] | None = None,
) -> tuple[dict, dict]:
    """Retorna (linha_home, linha_away) para fato_estatistica_selecao_partida."""
    flat = _flatten_por_key(groups)
    performance_points = performance_points or {}

    home_id = match["homeTeam"]["id"]
    away_id = match["awayTeam"]["id"]
    placar_home = match["homeScore"].get("current")
    placar_away = match["awayScore"].get("current")
    ht_home = match["homeScore"].get("period1")
    ht_away = match["awayScore"].get("period1")

    resultado_home = resultado_away = None
    if placar_home is not None and placar_away is not None:
        if placar_home > placar_away:
            resultado_home, resultado_away = "V", "D"
        elif placar_home < placar_away:
            resultado_home, resultado_away = "D", "V"
        else:
            resultado_home = resultado_away = "E"

    gols_2t_home = (placar_home - ht_home) if placar_home is not None and ht_home is not None else None
    gols_2t_away = (placar_away - ht_away) if placar_away is not None and ht_away is not None else None

    linha_home = _linha_para_lado(
        flat, "home", match["id"], home_id,
        placar_home, placar_away, resultado_home,
        ht_home, gols_2t_home, performance_points.get(home_id),
    )
    linha_away = _linha_para_lado(
        flat, "away", match["id"], away_id,
        placar_away, placar_home, resultado_away,
        ht_away, gols_2t_away, performance_points.get(away_id),
    )
    return linha_home, linha_away

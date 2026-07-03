"""
Resolver — partidas de uma seleção e detalhe de uma partida individual.
"""

from fastapi import HTTPException

from utils.query_executor import executar_query


def listar_partidas_selecao(selecao_id: int) -> dict:
    rows = executar_query("estatistica:select_by_selecao", params=(selecao_id,))
    if not rows:
        raise HTTPException(404, f"Nenhuma partida encontrada para a seleção {selecao_id}")

    partidas = []
    for r in rows:
        partidas.append({
            "partida_id": r["partida_id"],
            "tipo": r["tipo"],
            "status": r["status"],
            "data_partida": str(r["data_partida"]) if r["data_partida"] else None,
            "selecao_home_id": r["selecao_home_id"],
            "selecao_away_id": r["selecao_away_id"],
            "resultado": r["resultado"],
            "gols_marcados": r["gols_marcados"],
            "gols_sofridos": r["gols_sofridos"],
            "posse_bola": float(r["posse_bola"]) if r["posse_bola"] is not None else None,
            "chutes_total": r["chutes_total"],
            "chutes_no_gol": r["chutes_no_gol"],
            "escanteios": r["escanteios"],
            "cartoes_amarelos": r["cartoes_amarelos"],
            "cartoes_vermelhos": r["cartoes_vermelhos"],
            "performance_rating": float(r["performance_rating"]) if r["performance_rating"] is not None else None,
        })

    return {"selecao_id": selecao_id, "total": len(partidas), "partidas": partidas}


def buscar_partida(partida_id: int) -> dict:
    rows = executar_query("partida:select_by_id", params=(partida_id,))
    if not rows:
        raise HTTPException(404, f"Partida {partida_id} não encontrada")

    p = rows[0]
    estat = executar_query("estatistica:select_by_partida", params=(partida_id,))
    eventos = executar_query("evento:select_by_partida", params=(partida_id,))

    return {
        "id": p["id"],
        "custom_id": p["custom_id"],
        "selecao_home_id": p["selecao_home_id"],
        "selecao_away_id": p["selecao_away_id"],
        "placar_home": p["placar_home"],
        "placar_away": p["placar_away"],
        "placar_ht_home": p["placar_ht_home"],
        "placar_ht_away": p["placar_ht_away"],
        "status": p["status"],
        "vencedor_id": p["vencedor_id"],
        "tipo": p["tipo"],
        "grupo": p["grupo"],
        "rodada": p["rodada"],
        "data_partida": str(p["data_partida"]) if p["data_partida"] else None,
        "cidade": p["cidade"],
        "estatisticas": estat or [],
        "eventos": eventos or [],
    }

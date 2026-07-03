"""
Resolver — histórico de confrontos diretos (H2H) entre duas seleções.
"""

from fastapi import HTTPException

from utils.query_executor import executar_query


def buscar_h2h(selecao_a_id: int, selecao_b_id: int) -> dict:
    rows = executar_query(
        "h2h:select_by_selecoes",
        params=(selecao_a_id, selecao_b_id, selecao_b_id, selecao_a_id),
    )

    vitorias_a = sum(1 for r in rows if r["vencedor_id"] == selecao_a_id)
    vitorias_b = sum(1 for r in rows if r["vencedor_id"] == selecao_b_id)
    empates = sum(1 for r in rows if r["vencedor_id"] is None)

    confrontos = [
        {
            "id": r["id"],
            "selecao_a_id": r["selecao_a_id"],
            "selecao_b_id": r["selecao_b_id"],
            "placar_a": r["placar_a"],
            "placar_b": r["placar_b"],
            "vencedor_id": r["vencedor_id"],
            "torneio_nome": r["torneio_nome"],
            "data_partida": str(r["data_partida"]) if r["data_partida"] else None,
        }
        for r in rows
    ]

    return {
        "selecao_a_id": selecao_a_id,
        "selecao_b_id": selecao_b_id,
        "total_confrontos": len(rows),
        "vitorias_a": vitorias_a,
        "vitorias_b": vitorias_b,
        "empates": empates,
        "confrontos": confrontos,
    }

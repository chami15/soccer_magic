"""
Resolver — histórico de power ranking de uma seleção por rodada.
"""

from fastapi import HTTPException

from utils.query_executor import executar_query


def buscar_power_ranking(selecao_id: int) -> dict:
    rows = executar_query("power_ranking:select_by_selecao", params=(selecao_id,))
    if not rows:
        raise HTTPException(404, f"Nenhum dado de power ranking para a seleção {selecao_id}")

    historico = [
        {
            "round_id": r["round_id"],
            "round_num": r["round_num"],
            "round_nome": r["round_nome"],
            "rank": r["rank"],
            "pontos": r["pontos"],
            "rank_diff": r["rank_diff"],
        }
        for r in rows
    ]

    ultimo = historico[-1]

    return {
        "selecao_id": selecao_id,
        "rank_atual": ultimo["rank"],
        "pontos_atuais": ultimo["pontos"],
        "rank_diff_ultimo": ultimo["rank_diff"],
        "historico": historico,
    }

"""
Resolver — jogadores de uma seleção.
"""

from fastapi import HTTPException

from utils.query_executor import executar_query


def listar_jogadores_selecao(selecao_id: int) -> dict:
    rows = executar_query(
        "jogador:select_by_selecao",
        params=(selecao_id,),
    )
    if not rows:
        raise HTTPException(404, f"Nenhum jogador encontrado para a seleção {selecao_id}")

    jogadores = [
        {
            "id": r["id"],
            "nome": r["nome"],
            "nome_curto": r["nome_curto"],
            "posicao": r["posicao"],
            "numero_camisa": r["numero_camisa"],
            "valor_mercado": float(r["valor_mercado"]) if r["valor_mercado"] is not None else None,
            "moeda": r["moeda"],
        }
        for r in rows
    ]

    return {"selecao_id": selecao_id, "total": len(jogadores), "jogadores": jogadores}

"""
Persister — dim_jogador
"""

from utils.query_executor import executar_query


def upsert_jogador(row: dict) -> dict:
    resultado = executar_query(
        "jogador:upsert",
        returning=True,
        params=(
            row["id"],
            row["nome"],
            row["nome_curto"],
            row["posicao"],
            row["numero_camisa"],
            row["valor_mercado"],
            row["moeda"],
            row["selecao_id"],
        ),
    )
    return resultado[0] if resultado else {}


def upsert_jogadores(rows: list[dict]) -> list[dict]:
    return [upsert_jogador(row) for row in rows]

"""
Persister — fato_power_ranking_selecao
"""

from utils.query_executor import executar_query


def upsert_power_ranking(row: dict) -> dict:
    resultado = executar_query(
        "power_ranking:upsert",
        returning=True,
        params=(
            row["selecao_id"],
            row["round_id"],
            row["round_num"],
            row["round_nome"],
            row["rank"],
            row["pontos"],
            row["rank_diff"],
        ),
    )
    return resultado[0] if resultado else {}


def upsert_power_rankings(rows: list[dict]) -> list[dict]:
    return [upsert_power_ranking(row) for row in rows]

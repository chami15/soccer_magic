"""
Persister — fato_h2h_evento
"""

from utils.query_executor import executar_query


def upsert_h2h(row: dict) -> dict:
    resultado = executar_query(
        "h2h:upsert",
        returning=True,
        params=(
            row["id"],
            row["selecao_a_id"],
            row["selecao_b_id"],
            row["placar_a"],
            row["placar_b"],
            row["vencedor_id"],
            row["torneio_nome"],
            row["data_partida"],
            row["performance_a"],
            row["performance_b"],
        ),
    )
    return resultado[0] if resultado else {}


def upsert_h2hs(rows: list[dict]) -> list[dict]:
    return [upsert_h2h(row) for row in rows]

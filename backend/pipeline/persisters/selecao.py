"""
Persister — dim_selecao
Recebe linhas já transformadas (ver transformers/selecao.py) e grava no banco.
"""

from utils.query_executor import executar_query


def upsert_selecao(row: dict) -> dict:
    resultado = executar_query(
        "selecao:upsert",
        returning=True,
        params=(row["id"], row["nome"], row["continente"], row["grupo"], row["ranking_fifa"]),
    )
    return resultado[0] if resultado else {}


def upsert_selecoes(rows: list[dict]) -> list[dict]:
    return [upsert_selecao(row) for row in rows]

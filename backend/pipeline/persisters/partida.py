"""
Persister — fato_partida
"""

from utils.query_executor import executar_query


def upsert_partida(row: dict) -> dict:
    resultado = executar_query(
        "partida:upsert",
        returning=True,
        params=(
            row["id"],
            row["custom_id"],
            row["selecao_home_id"],
            row["selecao_away_id"],
            row["placar_home"],
            row["placar_away"],
            row["placar_ht_home"],
            row["placar_ht_away"],
            row["status"],
            row["vencedor_id"],
            row["tipo"],
            row["grupo"],
            row["rodada"],
            row["data_partida"],
            row["cidade"],
        ),
    )
    return resultado[0] if resultado else {}

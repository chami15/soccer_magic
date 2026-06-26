"""
Persister — fato_evento_partida
"""

from utils.query_executor import executar_query


def upsert_evento(row: dict) -> dict:
    resultado = executar_query(
        "evento:upsert",
        returning=True,
        params=(
            row["id"],
            row["partida_id"],
            row["selecao_id"],
            row["tipo_evento"],
            row["minuto"],
            row["minuto_extra"],
            row["jogador_id"],
            row["assistencia_jogador_id"],
            row["jogador_saida_id"],
            row["jogador_entrada_id"],
            row["tipo_gol"],
            row["var_decisao"],
        ),
    )
    return resultado[0] if resultado else {}


def upsert_eventos(rows: list[dict]) -> list[dict]:
    return [upsert_evento(row) for row in rows]

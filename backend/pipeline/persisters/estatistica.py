"""
Persister — fato_estatistica_selecao_partida
"""

from utils.query_executor import executar_query


def upsert_estatistica(row: dict) -> dict:
    resultado = executar_query(
        "estatistica:upsert",
        returning=True,
        params=(
            row["partida_id"],
            row["selecao_id"],
            row["resultado"],
            row["gols_marcados"],
            row["gols_sofridos"],
            row["posse_bola"],
            row["chutes_total"],
            row["chutes_no_gol"],
            row["chutes_bloqueados"],
            row["chutes_dentro_area"],
            row["chutes_fora_area"],
            row["escanteios"],
            row["impedimentos"],
            row["faltas"],
            row["cartoes_amarelos"],
            row["cartoes_vermelhos"],
            row["defesas"],
            row["passes_total"],
            row["passes_certos"],
            row["passes_precisao_pct"],
            row["gols_1_tempo"],
            row["gols_2_tempo"],
            row["performance_rating"],
        ),
    )
    return resultado[0] if resultado else {}


def upsert_estatisticas(rows: list[dict]) -> list[dict]:
    return [upsert_estatistica(row) for row in rows]

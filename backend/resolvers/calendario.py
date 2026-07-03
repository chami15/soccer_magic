"""
Resolver — calendário de próximas partidas da Copa.
Consulta diretamente o banco (fato_partida com status != 'finished'),
sem chamar a API do Sofascore em tempo real.
"""

from utils.query_executor import executar_query


def listar_proximas_partidas(limit: int = 20) -> dict:
    rows = executar_query("partida:select_proximas", params=(limit,))

    partidas = [
        {
            "id": r["id"],
            "selecao_home_id": r["selecao_home_id"],
            "selecao_home_nome": r.get("selecao_home_nome"),
            "selecao_away_id": r["selecao_away_id"],
            "selecao_away_nome": r.get("selecao_away_nome"),
            "status": r["status"],
            "tipo": r["tipo"],
            "grupo": r["grupo"],
            "rodada": r["rodada"],
            "data_partida": str(r["data_partida"]) if r["data_partida"] else None,
            "cidade": r["cidade"],
        }
        for r in rows
    ]

    return {"total": len(partidas), "partidas": partidas}

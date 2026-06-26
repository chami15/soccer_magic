"""
Transformer — dim_selecao
Converte o dict de time retornado por collector.get_wc_teams() no formato
de linha esperado por persisters/selecao.py.
"""

# TODO: continente ainda nao tem mapeamento (so "country" esta disponivel
# no payload do Sofascore). group_name e ranking_fifa ja vem prontos do
# collector (tournament.groupSign e team.ranking, respectivamente).

CONTINENTE_POR_PAIS = {
    # TODO: preencher o mapeamento pais -> continente conforme os 48 times
    # forem confirmados, ou trocar por uma lib/lookup table dedicada.
}


def transform_selecao(team: dict) -> dict:
    pais = team.get("country")
    return {
        "id": team["id"],
        "nome": team["name"],
        "continente": CONTINENTE_POR_PAIS.get(pais),
        "grupo": team.get("group_name"),
        "ranking_fifa": team.get("ranking_fifa"),
    }

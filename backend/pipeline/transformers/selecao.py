"""
Transformer — dim_selecao
Converte o dict de time retornado por collector.get_wc_teams() no formato
de linha esperado por persisters/selecao.py.
"""

# TODO: collector.get_wc_teams() ainda não extrai o grupo real (group_name
# sempre vem None) nem o continente (só "country" está disponível). Ambos
# precisam ser resolvidos no collector antes deste transformer ficar completo.

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

"""
Transformer — dim_jogador
Converte o objeto 'player' embutido num incidente de partida (gol, cartao,
substituicao — ver collector.get_match_incidents) na linha esperada por
persisters/jogador.py.

OBS: o objeto 'player' de dentro de um incidente e bem mais escasso que o
de um endpoint dedicado de elenco (sem numero de camisa/valor de mercado
confirmados) — por isso numero_camisa/valor_mercado/moeda ficam None aqui.
Se mais pra frente integrarmos /team/{id}/players, esses campos podem ser
preenchidos por um transformer mais completo.
"""


def transform_jogador(player: dict, selecao_id: int) -> dict:
    return {
        "id": player["id"],
        "nome": player.get("name", ""),
        "nome_curto": player.get("shortName"),
        "posicao": player.get("position"),
        "numero_camisa": None,
        "valor_mercado": None,
        "moeda": None,
        "selecao_id": selecao_id,
    }

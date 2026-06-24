"""
Transformer — dim_jogador
Converte o objeto 'player' embutido num incidente de partida (gol, cartao,
substituicao — ver collector.get_match_incidents) na linha esperada por
persisters/jogador.py.

Confirmado contra payload real: o objeto 'player'/'playerIn'/'playerOut'
de dentro de um incidente carrega 'jerseyNumber', 'marketValueCurrency' e
'proposedMarketValueRaw' (dict com 'value'/'currency').
"""


def transform_jogador(player: dict, selecao_id: int) -> dict:
    valor_mercado_raw = player.get("proposedMarketValueRaw") or {}
    return {
        "id": player["id"],
        "nome": player.get("name", ""),
        "nome_curto": player.get("shortName"),
        "posicao": player.get("position"),
        "numero_camisa": player.get("jerseyNumber"),
        "valor_mercado": valor_mercado_raw.get("value"),
        "moeda": player.get("marketValueCurrency"),
        "selecao_id": selecao_id,
    }

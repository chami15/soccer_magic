"""
Transformer — fato_power_ranking_selecao
Converte 1 item de collector.get_power_ranking_round() em linha da tabela.
round_meta vem de collector.get_power_ranking_rounds() (contem round_num/round_nome).
"""


def transform_power_ranking(item: dict, round_id: int, round_meta: dict) -> dict:
    round_info = round_meta.get("round", {})
    return {
        "selecao_id": item["team"]["id"],
        "round_id": round_id,
        "round_num": round_info.get("round"),
        "round_nome": round_info.get("name"),
        "rank": item["rank"],
        "pontos": item.get("points"),
        "rank_diff": item.get("rankDiff"),
    }

"""
Teste manual: busca o round atual de power ranking, encontra o Brasil
e persiste em fato_power_ranking_selecao usando o fluxo real
(collector -> transformer -> persister).

Rodar localmente:

    cd backend
    python3 test_insert_power_ranking.py
"""

import httpx

from pipeline import collector
from pipeline.transformers.power_ranking import transform_power_ranking
from pipeline.persisters.power_ranking import upsert_power_ranking

ROUND_ID = 134  # round 1 (pos-tournament-start); ver get_power_ranking_rounds() para o atual

if __name__ == "__main__":
    with httpx.Client() as client:
        rounds = collector.get_power_ranking_rounds(client)
        round_meta = next(r for r in rounds if r["id"] == ROUND_ID)
        print("round_meta:", round_meta)

        rankings = collector.get_power_ranking_round(client, ROUND_ID)

    brasil = next(item for item in rankings if item["team"]["id"] == 4748)
    print("dados brutos do collector:", brasil)

    row = transform_power_ranking(brasil, ROUND_ID, round_meta)
    print("transformado:", row)

    salvo = upsert_power_ranking(row)
    print("salvo:", salvo)

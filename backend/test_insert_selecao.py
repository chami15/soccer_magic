"""
Teste manual: busca o Brasil via collector, transforma e persiste em
dim_selecao usando o fluxo real (transformer -> persister).

Rodar localmente (fora do sandbox remoto, onde a porta do Postgres
nao e bloqueada):

    cd backend
    python3 test_insert_selecao.py
"""

import httpx

from pipeline import collector
from pipeline.transformers.selecao import transform_selecao
from pipeline.persisters.selecao import upsert_selecao

if __name__ == "__main__":
    with httpx.Client() as client:
        season_id = collector.get_wc_2026_season_id(client)
        teams = collector.get_wc_teams(client, season_id)

    brasil = next(t for t in teams if t["id"] == 4748)
    print("dados brutos do collector:", brasil)

    row = transform_selecao(brasil)
    print("transformado:", row)

    salvo = upsert_selecao(row)
    print("salvo:", salvo)

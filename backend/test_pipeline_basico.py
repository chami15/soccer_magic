"""
Teste manual escalonado: valida as 3 tabelas já com transformer/persister
prontos, end-to-end (collector -> transformer -> persister), usando o
Brasil como caso de teste:

  1. dim_selecao         (Brasil)
  2. fato_power_ranking_selecao (Brasil, round atual)
  3. fato_partida        (1 jogo recente do Brasil + o adversário,
                          que precisa existir em dim_selecao por causa
                          da FK NOT NULL)

Rodar localmente:

    cd backend
    python3 test_pipeline_basico.py
"""

import httpx

from pipeline import collector
from pipeline.transformers.selecao import transform_selecao
from pipeline.persisters.selecao import upsert_selecao
from pipeline.transformers.power_ranking import transform_power_ranking
from pipeline.persisters.power_ranking import upsert_power_ranking
from pipeline.transformers.partida import transform_partida
from pipeline.persisters.partida import upsert_partida

BRASIL_ID = 4748
POWER_RANKING_ROUND_ID = 134


def _team_minimo(team: dict) -> dict:
    """Adapta o objeto 'team' de dentro de um evento de partida (campos mais
    escassos que o de standings) para o formato esperado por transform_selecao."""
    return {
        "id": team["id"],
        "name": team.get("name", ""),
        "country": team.get("country", {}).get("name") if team.get("country") else None,
        "group_name": None,
        "ranking_fifa": team.get("ranking"),
    }


if __name__ == "__main__":
    with httpx.Client() as client:
        print("=== 1. dim_selecao (Brasil) ===")
        season_id = collector.get_wc_2026_season_id(client)
        teams = collector.get_wc_teams(client, season_id)
        brasil = next(t for t in teams if t["id"] == BRASIL_ID)
        row_selecao = transform_selecao(brasil)
        print("transformado:", row_selecao)
        print("salvo:", upsert_selecao(row_selecao))

        print("\n=== 2. fato_power_ranking_selecao (Brasil) ===")
        rounds = collector.get_power_ranking_rounds(client)
        round_meta = next(r for r in rounds if r["id"] == POWER_RANKING_ROUND_ID)
        rankings = collector.get_power_ranking_round(client, POWER_RANKING_ROUND_ID)
        brasil_ranking = next(item for item in rankings if item["team"]["id"] == BRASIL_ID)
        row_power = transform_power_ranking(brasil_ranking, POWER_RANKING_ROUND_ID, round_meta)
        print("transformado:", row_power)
        print("salvo:", upsert_power_ranking(row_power))

        print("\n=== 3. fato_partida (1 jogo recente do Brasil) ===")
        matches = collector.get_team_recent_matches(client, BRASIL_ID, count=1)
        match = matches[0]

        is_home = match["homeTeam"]["id"] == BRASIL_ID
        adversario = match["awayTeam"] if is_home else match["homeTeam"]
        row_adversario = transform_selecao(_team_minimo(adversario))
        print("adversario transformado:", row_adversario)
        print("adversario salvo:", upsert_selecao(row_adversario))

        row_partida = transform_partida(match)
        print("partida transformada:", row_partida)
        print("partida salva:", upsert_partida(row_partida))

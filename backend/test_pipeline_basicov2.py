"""
Teste manual escalonado v2: coleta os 2 jogos mais recentes do Brasil
e persiste end-to-end (collector -> transformer -> persister).

Diferença da v1: ao invés de processar apenas a última partida,
iteramos sobre os 2 jogos mais recentes, salvando para cada um:

  [uma vez, antes do loop]
  1. dim_selecao         (Brasil)
  2. fato_power_ranking_selecao (Brasil, round atual)

  [para cada uma das 2 partidas]
  3. dim_selecao         (adversário da partida)
  4. fato_partida
  5. fato_estatistica_selecao_partida (Brasil + adversário)
  6. dim_jogador + fato_evento_partida
  7. fato_h2h_evento     (histórico de confrontos entre os dois times)

Observações:
  - performance_points é coletado uma vez para o Brasil e reutilizado
    nas 2 partidas (o dict retornado cobre todos os match_ids do time).
  - O H2H é consultado por partida, pois cada jogo pode ter um adversário
    diferente com um histórico distinto.
  - O upsert garante idempotência: rodar o script mais de uma vez não
    duplica dados.

Rodar localmente:
    cd backend
    python3 test_pipeline_basicov2.py
"""

import httpx

from pipeline import collector
from pipeline.transformers.selecao import transform_selecao
from pipeline.persisters.selecao import upsert_selecao
from pipeline.transformers.power_ranking import transform_power_ranking
from pipeline.persisters.power_ranking import upsert_power_ranking
from pipeline.transformers.partida import transform_partida
from pipeline.persisters.partida import upsert_partida
from pipeline.transformers.estatistica import transform_estatistica
from pipeline.persisters.estatistica import upsert_estatistica
from pipeline.transformers.jogador import transform_jogador
from pipeline.persisters.jogador import upsert_jogador
from pipeline.transformers.evento import extrair_jogadores, transform_eventos
from pipeline.persisters.evento import upsert_evento
from pipeline.transformers.h2h import transform_h2h, extrair_adversarios
from pipeline.persisters.h2h import upsert_h2h

BRASIL_ID = 4748
POWER_RANKING_ROUND_ID = 134
NUM_MATCHES = 2


def _team_minimo(team: dict, group_sign: str | None = None) -> dict:
    """Adapta o objeto 'team' de dentro de um evento de partida para o
    formato esperado por transform_selecao."""
    return {
        "id": team["id"],
        "name": team.get("name", ""),
        "country": team.get("country", {}).get("name") if team.get("country") else None,
        "group_name": group_sign,
        "ranking_fifa": team.get("ranking"),
    }


def _group_sign_from_match(match: dict) -> str | None:
    sign = match.get("tournament", {}).get("groupSign")
    if sign:
        return sign
    group_name = match.get("tournament", {}).get("groupName") or ""
    return group_name.replace("Group ", "").strip() or None


if __name__ == "__main__":
    with httpx.Client() as client:

        # ── Etapa 1: dim_selecao (Brasil) — executada uma única vez ──────────
        print("=" * 60)
        print("=== 1. dim_selecao (Brasil) ===")
        print("=" * 60)
        season_id = collector.get_wc_2026_season_id(client)
        teams = collector.get_wc_teams(client, season_id)
        brasil = next(t for t in teams if t["id"] == BRASIL_ID)
        row_selecao = transform_selecao(brasil)
        print("transformado:", row_selecao)
        print("salvo:", upsert_selecao(row_selecao))

        # ── Etapa 2: power ranking (Brasil) — executada uma única vez ────────
        print("\n" + "=" * 60)
        print("=== 2. fato_power_ranking_selecao (Brasil) ===")
        print("=" * 60)
        rounds = collector.get_power_ranking_rounds(client)
        round_meta = next(r for r in rounds if r["id"] == POWER_RANKING_ROUND_ID)
        rankings = collector.get_power_ranking_round(client, POWER_RANKING_ROUND_ID)
        brasil_ranking = next(item for item in rankings if item["team"]["id"] == BRASIL_ID)
        row_power = transform_power_ranking(brasil_ranking, POWER_RANKING_ROUND_ID, round_meta)
        print("transformado:", row_power)
        print("salvo:", upsert_power_ranking(row_power))

        # ── Performance points do Brasil (cobre todos os match_ids do time) ──
        print("\nColetando performance points do Brasil...")
        try:
            performance_points = collector.get_team_performance_points(client, BRASIL_ID)
            print(f"{len(performance_points)} registros de performance encontrados.")
        except Exception as exc:
            print(f"Performance points não disponíveis: {exc}")
            performance_points = {}

        # ── Buscar os 2 jogos mais recentes ───────────────────────────────────
        print(f"\nBuscando os {NUM_MATCHES} jogos mais recentes do Brasil...")
        matches = collector.get_team_recent_matches(client, BRASIL_ID, count=NUM_MATCHES)
        print(f"{len(matches)} jogo(s) encontrado(s):")
        for idx, m in enumerate(matches):
            print(
                f"  [{idx + 1}] id={m['id']} | "
                f"{m['homeTeam']['name']} {m['homeScore'].get('current')} x "
                f"{m['awayScore'].get('current')} {m['awayTeam']['name']} | "
                f"{m.get('tournament', {}).get('name', 'torneio desconhecido')}"
            )

        # ── Loop pelas 2 partidas ─────────────────────────────────────────────
        for i, match in enumerate(matches):
            is_home = match["homeTeam"]["id"] == BRASIL_ID
            adversario = match["awayTeam"] if is_home else match["homeTeam"]
            group_sign = _group_sign_from_match(match)

            print(f"\n{'#' * 60}")
            print(
                f"### PARTIDA {i + 1}/{len(matches)}: "
                f"{match['homeTeam']['name']} {match['homeScore'].get('current')} x "
                f"{match['awayScore'].get('current')} {match['awayTeam']['name']} "
                f"(id={match['id']}) ###"
            )
            print(f"{'#' * 60}")

            # ── 3. dim_selecao adversário ─────────────────────────────────────
            print(f"\n--- 3.{i + 1} dim_selecao: {adversario['name']} ---")
            row_adv = transform_selecao(_team_minimo(adversario, group_sign))
            print("adversario transformado:", row_adv)
            print("adversario salvo:", upsert_selecao(row_adv))

            # ── 4. fato_partida ───────────────────────────────────────────────
            print(f"\n--- 4.{i + 1} fato_partida ---")
            row_partida = transform_partida(match)
            print("partida transformada:", row_partida)
            print("partida salva:", upsert_partida(row_partida))

            # ── 5. fato_estatistica_selecao_partida ───────────────────────────
            print(f"\n--- 5.{i + 1} fato_estatistica_selecao_partida ---")
            groups = collector.get_match_statistics(client, match["id"], match.get("customId"))
            print("groups brutos (primeiros 2):", groups[:2])
            linha_home, linha_away = transform_estatistica(groups, match, performance_points)
            print("home transformado:", linha_home)
            print("home salvo:", upsert_estatistica(linha_home))
            print("away transformado:", linha_away)
            print("away salvo:", upsert_estatistica(linha_away))

            # ── 6. dim_jogador + fato_evento_partida ──────────────────────────
            print(f"\n--- 6.{i + 1} dim_jogador + fato_evento_partida ---")
            incidents = collector.get_match_incidents(client, match["id"], match.get("customId"))
            print("incidentes brutos:", incidents)

            for player, selecao_id in extrair_jogadores(incidents, match):
                row_jogador = transform_jogador(player, selecao_id)
                print("jogador transformado:", row_jogador)
                print("jogador salvo:", upsert_jogador(row_jogador))

            for row_evento in transform_eventos(incidents, match):
                print("evento transformado:", row_evento)
                print("evento salvo:", upsert_evento(row_evento))

            # ── 7. fato_h2h_evento ────────────────────────────────────────────
            print(f"\n--- 7.{i + 1} fato_h2h_evento (Brasil x {adversario['name']}) ---")
            h2h_events = collector.get_h2h_events(client, match.get("customId"))
            print("eventos h2h brutos (primeiros 2):", h2h_events[:2])

            for adv_h2h in extrair_adversarios(h2h_events, BRASIL_ID):
                row_sel_h2h = transform_selecao(_team_minimo(adv_h2h))
                print("adversario h2h transformado:", row_sel_h2h)
                print("adversario h2h salvo:", upsert_selecao(row_sel_h2h))

            for event in h2h_events:
                row_h2h = transform_h2h(event, BRASIL_ID)
                print("h2h transformado:", row_h2h)
                print("h2h salvo:", upsert_h2h(row_h2h))

    print("\n" + "=" * 60)
    print("=== Teste v2 concluído ===")
    print("=" * 60)

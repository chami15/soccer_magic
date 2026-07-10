"""
Orquestrador do pipeline de ingestão.

Contém processar_time() — a função central que antes estava duplicada em
cada script test_pipeline_basicovN.py. Agora é importada de um único lugar.

Também expõe processar_partida_futura() para persistir jogos ainda não
disputados em fato_partida (necessário para o agente de análise).
"""

import sys
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from pipeline import collector
from pipeline.persisters.evento import upsert_evento
from pipeline.persisters.h2h import upsert_h2h
from pipeline.persisters.jogador import upsert_jogador
from pipeline.persisters.partida import upsert_partida
from pipeline.persisters.power_ranking import upsert_power_ranking
from pipeline.persisters.selecao import upsert_selecao
from pipeline.persisters.estatistica import upsert_estatistica
from pipeline.transformers.estatistica import transform_estatistica
from pipeline.transformers.evento import extrair_jogadores, transform_eventos
from pipeline.transformers.h2h import extrair_adversarios, transform_h2h
from pipeline.transformers.jogador import transform_jogador
from pipeline.transformers.partida import transform_partida
from pipeline.transformers.power_ranking import transform_power_ranking
from pipeline.transformers.selecao import transform_selecao


def _team_minimo(team: dict, group_sign: str | None = None) -> dict:
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


def processar_partida_futura(client: httpx.Client, match: dict) -> dict | None:
    """
    Persiste uma partida ainda não disputada em fato_partida.
    Garante que dim_selecao de ambos os times existe antes do INSERT.
    Retorna o dict salvo ou None em caso de erro.
    """
    try:
        home = match.get("homeTeam", {})
        away = match.get("awayTeam", {})
        group_sign = _group_sign_from_match(match)

        upsert_selecao(transform_selecao(_team_minimo(home, group_sign)))
        upsert_selecao(transform_selecao(_team_minimo(away, group_sign)))

        row = transform_partida(match)
        return upsert_partida(row)
    except Exception as exc:
        print(f"  ✗ Erro ao persistir partida futura id={match.get('id')}: {exc}")
        return None


def processar_time(
    client: httpx.Client,
    team: dict,
    rankings: list[dict],
    round_id: int,
    round_meta: dict,
    num_matches: int,
    label: str,
) -> dict:
    """
    Executa o pipeline completo para um time:
      dim_selecao → power ranking → últimos N jogos
        → por jogo: estatísticas, jogadores, eventos, h2h

    Retorna {"status": "ok"} ou {"status": "erro", "detalhe": ...}.
    Erros em partidas individuais são registrados mas não interrompem o fluxo.
    """
    team_id = team["id"]
    erros_partida = 0

    # ── 1. dim_selecao ────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"=== [{label}] 1. dim_selecao ===")
    print("=" * 60)
    row_selecao = transform_selecao(team)
    print("transformado:", row_selecao)
    print("salvo:", upsert_selecao(row_selecao))

    # ── 2. power ranking ──────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"=== [{label}] 2. fato_power_ranking_selecao ===")
    print("=" * 60)
    try:
        ranking_item = next(item for item in rankings if item["team"]["id"] == team_id)
        row_power = transform_power_ranking(ranking_item, round_id, round_meta)
        print("transformado:", row_power)
        print("salvo:", upsert_power_ranking(row_power))
    except StopIteration:
        print(f"  ⚠  {label} não encontrado no power ranking do round {round_id} — pulando.")

    # ── 3. performance points ─────────────────────────────────────────────────
    print(f"\nColetando performance points de {label}...")
    try:
        performance_points = collector.get_team_performance_points(client, team_id)
        print(f"{len(performance_points)} registros de performance encontrados.")
    except Exception as exc:
        print(f"Performance points não disponíveis: {exc}")
        performance_points = {}

    # ── 4. buscar últimas N partidas ──────────────────────────────────────────
    print(f"\nBuscando os {num_matches} jogos mais recentes de {label}...")
    matches = collector.get_team_recent_matches(client, team_id, count=num_matches)
    print(f"{len(matches)} jogo(s) encontrado(s):")
    for idx, m in enumerate(matches):
        print(
            f"  [{idx + 1}] id={m['id']} | "
            f"{m['homeTeam']['name']} {m['homeScore'].get('current')} x "
            f"{m['awayScore'].get('current')} {m['awayTeam']['name']} | "
            f"{m.get('tournament', {}).get('name', 'torneio desconhecido')}"
        )

    # ── Loop pelas partidas ───────────────────────────────────────────────────
    for i, match in enumerate(matches):
        try:
            is_home = match["homeTeam"]["id"] == team_id
            adversario = match["awayTeam"] if is_home else match["homeTeam"]
            group_sign = _group_sign_from_match(match)

            print(f"\n{'#' * 60}")
            print(
                f"### [{label}] PARTIDA {i + 1}/{len(matches)}: "
                f"{match['homeTeam']['name']} {match['homeScore'].get('current')} x "
                f"{match['awayScore'].get('current')} {match['awayTeam']['name']} "
                f"(id={match['id']}) ###"
            )
            print(f"{'#' * 60}")

            # 5. dim_selecao adversário
            print(f"\n--- [{label}] 5.{i+1} dim_selecao: {adversario['name']} ---")
            row_adv = transform_selecao(_team_minimo(adversario, group_sign))
            print("adversario transformado:", row_adv)
            print("adversario salvo:", upsert_selecao(row_adv))

            # 6. fato_partida
            print(f"\n--- [{label}] 6.{i+1} fato_partida ---")
            row_partida = transform_partida(match)
            print("partida transformada:", row_partida)
            print("partida salva:", upsert_partida(row_partida))

            # 7. fato_estatistica_selecao_partida
            print(f"\n--- [{label}] 7.{i+1} fato_estatistica_selecao_partida ---")
            groups = collector.get_match_statistics(client, match["id"], match.get("customId"))
            print("groups brutos (primeiros 2):", groups[:2])
            linha_home, linha_away = transform_estatistica(groups, match, performance_points)
            print("home transformado:", linha_home)
            print("home salvo:", upsert_estatistica(linha_home))
            print("away transformado:", linha_away)
            print("away salvo:", upsert_estatistica(linha_away))

            # 8. dim_jogador + fato_evento_partida
            print(f"\n--- [{label}] 8.{i+1} dim_jogador + fato_evento_partida ---")
            incidents = collector.get_match_incidents(client, match["id"], match.get("customId"))
            print("incidentes brutos:", incidents)

            for player, selecao_id in extrair_jogadores(incidents, match):
                row_jogador = transform_jogador(player, selecao_id)
                print("jogador transformado:", row_jogador)
                print("jogador salvo:", upsert_jogador(row_jogador))

            for row_evento in transform_eventos(incidents, match):
                print("evento transformado:", row_evento)
                print("evento salvo:", upsert_evento(row_evento))

            # 9. fato_h2h_evento
            print(f"\n--- [{label}] 9.{i+1} fato_h2h_evento ({label} x {adversario['name']}) ---")
            h2h_events = collector.get_h2h_events(client, match.get("customId"))
            print("eventos h2h brutos (primeiros 2):", h2h_events[:2])

            for adv_h2h in extrair_adversarios(h2h_events, team_id):
                row_sel_h2h = transform_selecao(_team_minimo(adv_h2h))
                print("adversario h2h transformado:", row_sel_h2h)
                print("adversario h2h salvo:", upsert_selecao(row_sel_h2h))

            for event in h2h_events:
                row_h2h = transform_h2h(event, team_id)
                print("h2h transformado:", row_h2h)
                print("h2h salvo:", upsert_h2h(row_h2h))

        except Exception as exc:
            erros_partida += 1
            print(
                f"  ✗  [{label}] erro ao processar partida {i+1}/{len(matches)} "
                f"(id={match.get('id')}): {exc}"
            )
            continue

    status = "ok" if erros_partida == 0 else f"concluído com {erros_partida} erro(s) em {len(matches)} partida(s)"
    print(f"\n[{label}] {status}")
    return {"status": status, "label": label, "team_id": team_id}

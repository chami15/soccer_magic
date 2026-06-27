"""
Teste manual escalonado v11: coleta os 5 jogos mais recentes de cada uma das
12 seleções que jogam amanhã (6 partidas), persistindo tudo end-to-end.

Mesma função processar_time() das versões v4–v10. Diferença: como são 12
times de uma vez (volume bem maior que o par único das versões anteriores),
cada time é processado dentro de um try/except isolado, para que uma falha
num time (ou numa partida específica) não interrompa o processamento dos
demais. Ao final é impresso um resumo de sucesso/erro por time.

Optou-se por manter o processamento síncrono e sequencial (mesma base do
collector, que usa httpx.Client). Migrar para httpx.AsyncClient/asyncio
exigiria reescrever collector, transformers e persisters só para este script
de teste pontual — custo alto para o ganho, já que a carga (12 times) ainda
é pequena. Se o volume crescer bastante no futuro, vale revisitar.

Jogos de amanhã:
    Panamá        x Inglaterra
    Croácia       x Gana
    Colômbia      x Portugal
    RD Congo      x Uzbequistão
    Argélia       x Áustria
    Jordânia      x Argentina

Rodar localmente:
    cd backend
    python3 test_pipeline_basicov11.py
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

POWER_RANKING_ROUND_ID = 134
NUM_MATCHES = 5

# (kwargs de busca do time, label de exibição)
TIMES_BUSCA = [
    (("Panama", "Panamá"), "Panamá"),
    (("England", "Inglaterra"), "Inglaterra"),
    (("Croatia", "Croácia", "Croacia"), "Croácia"),
    (("Ghana", "Gana"), "Gana"),
    (("Colombia", "Colômbia"), "Colômbia"),
    (("Portugal",), "Portugal"),
    (("DR Congo", "Congo DR", "RD Congo", "República Democrática do Congo"), "RD Congo"),
    (("Uzbekistan", "Uzbequistão", "Uzbesquistão"), "Uzbequistão"),
    (("Algeria", "Argélia", "Argelia"), "Argélia"),
    (("Austria", "Áustria"), "Áustria"),
    (("Jordan", "Jordânia", "Jordania"), "Jordânia"),
    (("Argentina",), "Argentina"),
]


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


def localizar_time(teams: list[dict], keywords: tuple[str, ...], label: str) -> dict:
    try:
        return next(
            t for t in teams
            if any(kw in t.get("name", "") for kw in keywords)
        )
    except StopIteration:
        raise RuntimeError(
            f"Time '{label}' não encontrado na lista de times da Copa "
            f"(keywords testadas: {keywords})"
        )


def processar_time(
    client: httpx.Client,
    team: dict,
    rankings: list[dict],
    round_id: int,
    round_meta: dict,
    num_matches: int,
    label: str,
) -> None:
    """Executa o pipeline completo (dim_selecao → power ranking → N partidas) para um time."""
    team_id = team["id"]

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
    erros_partida = 0
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

            # ── 5. dim_selecao adversário ─────────────────────────────────────
            print(f"\n--- [{label}] 5.{i + 1} dim_selecao: {adversario['name']} ---")
            row_adv = transform_selecao(_team_minimo(adversario, group_sign))
            print("adversario transformado:", row_adv)
            print("adversario salvo:", upsert_selecao(row_adv))

            # ── 6. fato_partida ───────────────────────────────────────────────
            print(f"\n--- [{label}] 6.{i + 1} fato_partida ---")
            row_partida = transform_partida(match)
            print("partida transformada:", row_partida)
            print("partida salva:", upsert_partida(row_partida))

            # ── 7. fato_estatistica_selecao_partida ───────────────────────────
            print(f"\n--- [{label}] 7.{i + 1} fato_estatistica_selecao_partida ---")
            groups = collector.get_match_statistics(client, match["id"], match.get("customId"))
            print("groups brutos (primeiros 2):", groups[:2])
            linha_home, linha_away = transform_estatistica(groups, match, performance_points)
            print("home transformado:", linha_home)
            print("home salvo:", upsert_estatistica(linha_home))
            print("away transformado:", linha_away)
            print("away salvo:", upsert_estatistica(linha_away))

            # ── 8. dim_jogador + fato_evento_partida ──────────────────────────
            print(f"\n--- [{label}] 8.{i + 1} dim_jogador + fato_evento_partida ---")
            incidents = collector.get_match_incidents(client, match["id"], match.get("customId"))
            print("incidentes brutos:", incidents)

            for player, selecao_id in extrair_jogadores(incidents, match):
                row_jogador = transform_jogador(player, selecao_id)
                print("jogador transformado:", row_jogador)
                print("jogador salvo:", upsert_jogador(row_jogador))

            for row_evento in transform_eventos(incidents, match):
                print("evento transformado:", row_evento)
                print("evento salvo:", upsert_evento(row_evento))

            # ── 9. fato_h2h_evento ────────────────────────────────────────────
            print(f"\n--- [{label}] 9.{i + 1} fato_h2h_evento ({label} x {adversario['name']}) ---")
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
                f"  ✗  [{label}] erro ao processar partida {i + 1}/{len(matches)} "
                f"(id={match.get('id')}): {exc}"
            )
            continue

    if erros_partida:
        print(f"\n[{label}] concluído com {erros_partida} partida(s) com erro de {len(matches)}.")
    else:
        print(f"\n[{label}] concluído sem erros ({len(matches)} partida(s)).")


if __name__ == "__main__":
    resultados: dict[str, str] = {}

    with httpx.Client() as client:

        # ── Dados globais — carregados uma única vez ───────────────────────────
        print("=" * 60)
        print("=== Carregando dados globais (times + power ranking) ===")
        print("=" * 60)

        season_id = collector.get_wc_2026_season_id(client)
        teams = collector.get_wc_teams(client, season_id)

        # Power ranking — carregado uma vez e compartilhado entre todos os times
        rounds = collector.get_power_ranking_rounds(client)
        round_meta = next(r for r in rounds if r["id"] == POWER_RANKING_ROUND_ID)
        rankings = collector.get_power_ranking_round(client, POWER_RANKING_ROUND_ID)
        print(f"Power ranking round {POWER_RANKING_ROUND_ID} carregado: {len(rankings)} times.")

        # ── Localizar os 12 times nos dados da Copa ─────────────────────────────
        print(f"\n{'=' * 60}")
        print("=== Localizando os 12 times dos jogos de amanhã ===")
        print("=" * 60)

        times_localizados: list[tuple[dict, str]] = []
        for keywords, label in TIMES_BUSCA:
            try:
                time_encontrado = localizar_time(teams, keywords, label)
                print(f"  ✓ {label}: id={time_encontrado['id']} nome={time_encontrado['name']}")
                times_localizados.append((time_encontrado, label))
            except RuntimeError as exc:
                print(f"  ✗ {exc}")
                resultados[label] = f"erro: não localizado ({exc})"

        # ── Pipeline completo, time a time ──────────────────────────────────────
        for time_encontrado, label in times_localizados:
            print(f"\n{'*' * 60}")
            print(f"*** PROCESSANDO: {label.upper()} ***")
            print(f"{'*' * 60}")
            try:
                processar_time(
                    client=client,
                    team=time_encontrado,
                    rankings=rankings,
                    round_id=POWER_RANKING_ROUND_ID,
                    round_meta=round_meta,
                    num_matches=NUM_MATCHES,
                    label=label,
                )
                resultados[label] = "ok"
            except Exception as exc:
                print(f"  ✗  [{label}] FALHA no processamento do time: {exc}")
                resultados[label] = f"erro: {exc}"

    # ── Resumo final ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("=== Resumo v11 ===")
    print("=" * 60)
    for label, status in resultados.items():
        marcador = "✓" if status == "ok" else "✗"
        print(f"  {marcador} {label}: {status}")

    total_ok = sum(1 for s in resultados.values() if s == "ok")
    print(f"\n{total_ok}/{len(TIMES_BUSCA)} times processados com sucesso.")
    print("=" * 60)
    print("=== Teste v11 concluído ===")
    print("=" * 60)

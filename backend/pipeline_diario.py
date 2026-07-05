"""
Pipeline Diário — Soccer Magic

Descobre os jogos da Copa que acontecem amanhã, executa o pipeline
completo de ingestão para cada seleção envolvida (últimos 5 jogos +
power ranking + h2h + eventos) e persiste a partida futura no banco
para que o agente de análise possa ser ativado pelo frontend.

Rodar manualmente:
    cd backend
    python3 pipeline_diario.py

Em produção, agendar via cron ou GitHub Actions (ex: todo dia às 06h00):
    0 6 * * * cd /path/to/backend && python3 pipeline_diario.py >> logs/pipeline_diario.log 2>&1
"""

import datetime
import httpx

from pipeline import collector
from pipeline.orquestrador import processar_partida_futura, processar_time

POWER_RANKING_ROUND_ID = 134
NUM_MATCHES = 5


def _amanha_timestamp() -> tuple[int, int]:
    """Retorna (inicio_amanha, fim_amanha) como Unix timestamps UTC.
    Usa a data local da máquina para determinar 'amanhã', evitando que
    fusos negativos (ex: UTC-3) avancem o dia incorretamente."""
    amanha = datetime.date.today() + datetime.timedelta(days=1)
    # Constrói os limites em UTC explícito (timezone-aware) para evitar
    # comportamento ambíguo do timestamp() em sistemas com TZ != UTC.
    tz_utc = datetime.timezone.utc
    inicio = int(datetime.datetime(amanha.year, amanha.month, amanha.day, 0, 0, 0, tzinfo=tz_utc).timestamp())
    fim = int(datetime.datetime(amanha.year, amanha.month, amanha.day, 23, 59, 59, tzinfo=tz_utc).timestamp())
    return inicio, fim


def filtrar_jogos_amanha(eventos: list[dict]) -> list[dict]:
    """Filtra apenas os eventos cuja startTimestamp cai dentro de amanhã (UTC)."""
    inicio, fim = _amanha_timestamp()
    return [
        e for e in eventos
        if inicio <= e.get("startTimestamp", 0) <= fim
    ]


def extrair_times_dos_jogos(jogos: list[dict]) -> list[dict]:
    """Extrai lista de times únicos a partir dos jogos (home + away, sem repetição)."""
    vistos: set[int] = set()
    times: list[dict] = []
    for jogo in jogos:
        for lado in ("homeTeam", "awayTeam"):
            time = jogo.get(lado, {})
            tid = time.get("id")
            if tid and tid not in vistos:
                vistos.add(tid)
                times.append(time)
    return times


def main() -> None:
    resultados: dict[str, str] = {}

    with httpx.Client() as client:
        print("=" * 60)
        print("=== PIPELINE DIÁRIO — Soccer Magic ===")
        print(f"=== Executado em: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} ===")
        print("=" * 60)

        # ── 1. Descobrir todos os próximos jogos da Copa ──────────────────────
        print("\nBuscando próximos eventos da Copa...")
        todos_proximos = collector.get_tournament_next_events(client)
        jogos_amanha = filtrar_jogos_amanha(todos_proximos)

        print(f"{len(todos_proximos)} jogo(s) futuros encontrados no calendário da Copa.")
        if not todos_proximos:
            print("Nenhum jogo futuro encontrado. Encerrando.")
            return
        if not jogos_amanha:
            print("Nenhum jogo encontrado para amanhã — calendário será atualizado mesmo assim.")
        else:
            print(f"\n{len(jogos_amanha)} jogo(s) encontrado(s) para amanhã:")
            for j in jogos_amanha:
                ts = j.get("startTimestamp", 0)
                hora = datetime.datetime.utcfromtimestamp(ts).strftime("%H:%M UTC")
                print(
                    f"  id={j['id']} | "
                    f"{j.get('homeTeam', {}).get('name', '?')} x "
                    f"{j.get('awayTeam', {}).get('name', '?')} | {hora}"
                )

        # ── 2. Carregar dados globais (power ranking) ─────────────────────────
        print("\nCarregando power ranking...")
        rounds = collector.get_power_ranking_rounds(client)
        round_meta = next((r for r in rounds if r["id"] == POWER_RANKING_ROUND_ID), None)
        if round_meta is None:
            print(f"  ⚠  Round {POWER_RANKING_ROUND_ID} não encontrado — usando último disponível.")
            round_meta = rounds[-1] if rounds else {}
            round_id = round_meta.get("id", POWER_RANKING_ROUND_ID)
        else:
            round_id = POWER_RANKING_ROUND_ID

        rankings = collector.get_power_ranking_round(client, round_id)
        print(f"Power ranking round {round_id} carregado: {len(rankings)} times.")

        # ── 3. Persistir TODOS os jogos futuros no calendário ────────────────
        print(f"\n{'=' * 60}")
        print("=== Persistindo calendário completo em fato_partida ===")
        print("=" * 60)
        calendario_ok = 0
        for jogo in todos_proximos:
            resultado = processar_partida_futura(client, jogo)
            if resultado:
                calendario_ok += 1
        print(f"  {calendario_ok}/{len(todos_proximos)} partidas futuras persistidas no calendário.")

        # ── 4. Pipeline completo para cada seleção que joga amanhã ───────────
        if not jogos_amanha:
            print("\nSem seleções para processar hoje. Encerrando após salvar calendário.")
            return

        times = extrair_times_dos_jogos(jogos_amanha)
        print(f"\n{'=' * 60}")
        print(f"=== Processando {len(times)} seleções ===")
        print("=" * 60)

        for time in times:
            label = time.get("name", f"id={time.get('id')}")
            print(f"\n{'*' * 60}")
            print(f"*** PROCESSANDO: {label.upper()} ***")
            print(f"{'*' * 60}")
            try:
                resultado = processar_time(
                    client=client,
                    team=time,
                    rankings=rankings,
                    round_id=round_id,
                    round_meta=round_meta,
                    num_matches=NUM_MATCHES,
                    label=label,
                )
                resultados[label] = resultado["status"]
            except Exception as exc:
                print(f"  ✗  [{label}] FALHA: {exc}")
                resultados[label] = f"erro: {exc}"

    # ── Resumo final ──────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("=== Resumo do pipeline diário ===")
    print("=" * 60)
    for label, status in resultados.items():
        marcador = "✓" if status == "ok" else "✗"
        print(f"  {marcador} {label}: {status}")

    total_ok = sum(1 for s in resultados.values() if s == "ok")
    print(f"\n{total_ok}/{len(resultados)} seleções processadas com sucesso.")
    print("=" * 60)
    print("=== Pipeline diário concluído ===")
    print("=" * 60)


if __name__ == "__main__":
    main()

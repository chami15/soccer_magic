"""
Teste rápido: busca os jogos de amanhã via Sofascore (sem banco).
Rodar: python testar_jogos_amanha.py
"""
import datetime
import httpx

from pipeline import collector
from pipeline_diario import filtrar_jogos_amanha

tz_utc = datetime.timezone.utc

with httpx.Client() as client:
    print("Buscando próximos eventos da Copa...")
    todos = collector.get_tournament_next_events(client)
    amanha = filtrar_jogos_amanha(todos)

    amanha_data = datetime.date.today() + datetime.timedelta(days=1)
    print(f"\nTotal de jogos futuros na Copa: {len(todos)}")
    print(f"Jogos de amanha ({amanha_data}): {len(amanha)}")

    if amanha:
        print("\nPartidas de amanha:")
        for j in amanha:
            ts = j.get("startTimestamp", 0)
            hora = datetime.datetime.fromtimestamp(ts, tz=tz_utc).strftime("%H:%M UTC")
            home = j["homeTeam"]["name"]
            away = j["awayTeam"]["name"]
            print(f"  id={j['id']} | {home} x {away} | {hora}")
    else:
        print("\nNenhum jogo encontrado para amanha.")
        print("\nPrimeiros 5 jogos futuros (qualquer data):")
        for j in todos[:5]:
            ts = j.get("startTimestamp", 0)
            data = datetime.datetime.fromtimestamp(ts, tz=tz_utc).strftime("%Y-%m-%d %H:%M UTC")
            home = j["homeTeam"]["name"]
            away = j["awayTeam"]["name"]
            print(f"  id={j['id']} | {home} x {away} | {data}")

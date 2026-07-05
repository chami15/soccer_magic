"""
Testa se o collector consegue buscar H2H entre dois times.
Usa um customId de uma partida real que já está no banco.

Rodar:
    python testar_h2h_collector.py

O customId vem do campo custom_id em fato_partida. Se não souber,
deixe o script descobrir automaticamente pelos últimos jogos coletados.
"""
import httpx

from pipeline import collector
from utils.query_executor import executar_query


def main():
    print("Buscando partidas no banco para pegar um customId...")
    rows = executar_query(
        "partida:select_proximas", params=(5,)
    )

    if not rows:
        print("Nenhuma partida encontrada no banco. Rode o pipeline_diario.py primeiro.")
        return

    # Pega a primeira com custom_id preenchido
    partida = next((r for r in rows if r.get("custom_id")), None)
    if not partida:
        # Tenta buscar partidas finalizadas
        rows_fin = executar_query(
            "SELECT id, custom_id, selecao_home_id, selecao_away_id, selecao_home_nome, selecao_away_nome "
            "FROM fato_partida p "
            "LEFT JOIN dim_selecao h ON h.id = p.selecao_home_id "
            "LEFT JOIN dim_selecao a ON a.id = p.selecao_away_id "
            "WHERE custom_id IS NOT NULL LIMIT 5",
            params=()
        )
        partida = rows_fin[0] if rows_fin else None

    if not partida:
        print("Nenhuma partida com customId encontrada. Verifique o banco.")
        return

    custom_id = partida.get("custom_id")
    home = partida.get("selecao_home_nome") or partida.get("selecao_home_id")
    away = partida.get("selecao_away_nome") or partida.get("selecao_away_id")

    print(f"\nPartida selecionada: {home} x {away}")
    print(f"customId: {custom_id}")
    print(f"\nBuscando H2H em /event/{custom_id}/h2h/events ...")

    with httpx.Client() as client:
        eventos = collector.get_h2h_events(client, custom_id)

    print(f"\nTotal de confrontos diretos encontrados: {len(eventos)}")

    if not eventos:
        print("\nNenhum H2H encontrado. Possíveis causas:")
        print("  - Times nunca se enfrentaram na história (ex: Brasil x Noruega)")
        print("  - O customId pode estar incorreto")
        print("  - O Sofascore não tem registro histórico deste confronto")
    else:
        print("\nPrimeiros 3 confrontos:")
        from pipeline.transformers.h2h import _score
        for e in eventos[:3]:
            home_e = e.get("homeTeam", {}).get("name", "?")
            away_e = e.get("awayTeam", {}).get("name", "?")
            h = _score(e.get("homeScore")) if e.get("homeScore") else "?"
            a = _score(e.get("awayScore")) if e.get("awayScore") else "?"
            torneio = e.get("tournament", {}).get("name", "?")
            print(f"  {home_e} {h} x {a} {away_e} | {torneio}")


if __name__ == "__main__":
    main()

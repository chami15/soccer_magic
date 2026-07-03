"""
Tools do agente de análise de partidas.

Cada tool consulta o banco via query_executor (mesmo padrão dos resolvers)
ou executa cálculos estatísticos via probabilidades.py.

Inputs validados por Pydantic (args_schema). Outputs sempre como dict
com chave 'status': 'ok' | 'erro' para o agente saber se pode confiar no dado.
"""

from langchain.tools import tool
from pydantic import BaseModel, Field

from agente.probabilidades import rodar_modelo_completo
from utils.query_executor import executar_query


# ─── Input schemas ────────────────────────────────────────────────────────────

class PartidaInput(BaseModel):
    partida_id: int = Field(..., description="ID numérico da partida no banco (Sofascore).")

class SelecaoInput(BaseModel):
    selecao_id: int = Field(..., description="ID numérico da seleção no banco (Sofascore).")

class H2HInput(BaseModel):
    selecao_a_id: int = Field(..., description="ID da primeira seleção.")
    selecao_b_id: int = Field(..., description="ID da segunda seleção.")

class ModeloGolsInput(BaseModel):
    selecao_home_id: int = Field(..., description="ID da seleção mandante.")
    selecao_away_id: int = Field(..., description="ID da seleção visitante.")


# ─── Tools ───────────────────────────────────────────────────────────────────

@tool(args_schema=PartidaInput)
def get_match_context(partida_id: int) -> dict:
    """
    Retorna o contexto completo de uma partida: times, placar, status,
    tipo (Copa/Amistoso), grupo, rodada, cidade e data.
    SEMPRE chame esta tool primeiro antes de qualquer outra.
    """
    rows = executar_query("partida:select_by_id", params=(partida_id,))
    if not rows:
        return {"status": "erro", "detalhe": f"Partida {partida_id} não encontrada no banco."}

    p = rows[0]

    home_rows = executar_query("selecao:select_by_id", params=(p["selecao_home_id"],))
    away_rows = executar_query("selecao:select_by_id", params=(p["selecao_away_id"],))

    return {
        "status": "ok",
        "partida_id": p["id"],
        "selecao_home_id": p["selecao_home_id"],
        "selecao_home_nome": home_rows[0]["nome"] if home_rows else "Desconhecido",
        "selecao_away_id": p["selecao_away_id"],
        "selecao_away_nome": away_rows[0]["nome"] if away_rows else "Desconhecido",
        "status_partida": p["status"],
        "tipo": p["tipo"],
        "grupo": p["grupo"],
        "rodada": p["rodada"],
        "data_partida": str(p["data_partida"]) if p["data_partida"] else None,
        "cidade": p["cidade"],
    }


@tool(args_schema=SelecaoInput)
def get_team_stats(selecao_id: int) -> dict:
    """
    Retorna as estatísticas agregadas da seleção: médias de gols, posse,
    chutes, escanteios, cartões, faltas, defesas, passes, forma recente,
    percentuais over/under, BTTS, clean sheets e qualidade dos dados.
    Chame para AMBAS as seleções (home e away) antes do modelo de gols.
    """
    rows = executar_query("estatistica:select_by_selecao", params=(selecao_id,))
    if not rows:
        return {
            "status": "erro",
            "detalhe": f"Sem estatísticas para seleção {selecao_id}. "
                       "Prossiga com dados limitados.",
        }

    import pandas as pd
    df = pd.DataFrame(rows)
    df = df.sort_values("data_partida", ascending=False)

    copa = df[df["tipo"] == "Copa"]
    amistoso = df[df["tipo"] != "Copa"]
    faltam = 5 - len(copa)
    janela = pd.concat([copa, amistoso.head(max(faltam, 0))]).head(5)

    n = len(janela)

    def media(col):
        return round(float(janela[col].mean()), 2) if col in janela.columns and n > 0 else None

    total_gols = janela["gols_marcados"] + janela["gols_sofridos"]

    forma = []
    for _, row in janela.iterrows():
        venc = row.get("resultado")
        forma.append(venc if venc else "?")

    return {
        "status": "ok",
        "selecao_id": selecao_id,
        "jogos_na_janela": n,
        "data_quality": "insufficient" if n < 3 else ("partial" if n < 5 else "complete"),
        "forma": " ".join(forma),
        "avg_gols_marcados": media("gols_marcados"),
        "avg_gols_sofridos": media("gols_sofridos"),
        "avg_posse": media("posse_bola"),
        "avg_chutes_total": media("chutes_total"),
        "avg_chutes_no_gol": media("chutes_no_gol"),
        "avg_escanteios": media("escanteios"),
        "avg_amarelos": media("cartoes_amarelos"),
        "avg_vermelhos": media("cartoes_vermelhos"),
        "avg_faltas": media("faltas"),
        "avg_defesas": media("defesas"),
        "avg_passes_total": media("passes_total"),
        "avg_passes_certos": media("passes_certos"),
        "avg_gols_1t": media("gols_1_tempo"),
        "avg_gols_2t": media("gols_2_tempo"),
        "over15_pct": round(float((total_gols >= 2).mean() * 100), 2) if n > 0 else None,
        "over25_pct": round(float((total_gols >= 3).mean() * 100), 2) if n > 0 else None,
        "over35_pct": round(float((total_gols >= 4).mean() * 100), 2) if n > 0 else None,
        "btts_pct": round(
            float(
                ((janela["gols_marcados"] > 0) & (janela["gols_sofridos"] > 0)).mean() * 100
            ), 2
        ) if n > 0 else None,
        "clean_sheets": int((janela["gols_sofridos"] == 0).sum()) if n > 0 else 0,
        "over35_corners_pct": media("escanteios"),
    }


@tool(args_schema=H2HInput)
def get_h2h(selecao_a_id: int, selecao_b_id: int) -> dict:
    """
    Retorna o histórico de confrontos diretos entre duas seleções:
    total de jogos, vitórias de cada lado, empates e os últimos confrontos.
    Use para calibrar a probabilidade do resultado final.
    """
    rows = executar_query(
        "h2h:select_by_selecoes",
        params=(selecao_a_id, selecao_b_id, selecao_b_id, selecao_a_id),
    )
    if not rows:
        return {
            "status": "ok",
            "aviso": "Sem histórico H2H disponível.",
            "total": 0,
            "vitorias_a": 0,
            "vitorias_b": 0,
            "empates": 0,
            "ultimos_confrontos": [],
        }

    vitorias_a = sum(1 for r in rows if r["vencedor_id"] == selecao_a_id)
    vitorias_b = sum(1 for r in rows if r["vencedor_id"] == selecao_b_id)
    empates = sum(1 for r in rows if r["vencedor_id"] is None)

    ultimos = [
        {
            "data": str(r["data_partida"]) if r["data_partida"] else None,
            "placar": f"{r['placar_a']}-{r['placar_b']}",
            "vencedor_id": r["vencedor_id"],
            "torneio": r["torneio_nome"],
        }
        for r in rows[:5]
    ]

    return {
        "status": "ok",
        "selecao_a_id": selecao_a_id,
        "selecao_b_id": selecao_b_id,
        "total": len(rows),
        "vitorias_a": vitorias_a,
        "vitorias_b": vitorias_b,
        "empates": empates,
        "ultimos_confrontos": ultimos,
    }


@tool(args_schema=SelecaoInput)
def get_power_ranking(selecao_id: int) -> dict:
    """
    Retorna o histórico de power ranking da seleção por rodada.
    Indica momentum (se está subindo ou caindo no ranking).
    """
    rows = executar_query("power_ranking:select_by_selecao", params=(selecao_id,))
    if not rows:
        return {
            "status": "ok",
            "aviso": "Sem dados de power ranking para esta seleção.",
            "rank_atual": None,
            "tendencia": None,
        }

    ultimo = rows[-1]
    tendencia = None
    if len(rows) >= 2:
        diff = rows[-1]["rank"] - rows[-2]["rank"]
        tendencia = "subindo" if diff < 0 else ("caindo" if diff > 0 else "estavel")

    return {
        "status": "ok",
        "selecao_id": selecao_id,
        "rank_atual": ultimo["rank"],
        "pontos_atuais": ultimo["pontos"],
        "rank_diff_ultimo": ultimo.get("rank_diff"),
        "tendencia": tendencia,
        "historico": [
            {
                "round_num": r["round_num"],
                "rank": r["rank"],
                "pontos": r["pontos"],
            }
            for r in rows
        ],
    }


@tool(args_schema=ModeloGolsInput)
def calcular_modelo_gols(selecao_home_id: int, selecao_away_id: int) -> dict:
    """
    Executa o modelo de Poisson com os dados do banco e retorna as
    probabilidades de todos os mercados: 1X2, over/under 1.5/2.5/3.5/4.5,
    BTTS, placar mais provável (top 3), cartões amarelos e escanteios.
    Chame esta tool APÓS get_team_stats para ambas as seleções.
    Esta é a tool central da análise — chame-a apenas UMA vez.
    """
    home_rows = executar_query("estatistica:select_by_selecao", params=(selecao_home_id,))
    away_rows = executar_query("estatistica:select_by_selecao", params=(selecao_away_id,))

    def extrair_medias(rows):
        if not rows:
            return {}
        import pandas as pd
        df = pd.DataFrame(rows).sort_values("data_partida", ascending=False)
        copa = df[df["tipo"] == "Copa"]
        amistoso = df[df["tipo"] != "Copa"]
        faltam = 5 - len(copa)
        janela = pd.concat([copa, amistoso.head(max(faltam, 0))]).head(5)
        if janela.empty:
            return {}

        def m(col):
            return float(janela[col].mean()) if col in janela.columns else None

        return {
            "avg_gols_marcados": m("gols_marcados") or 1.0,
            "avg_gols_sofridos": m("gols_sofridos") or 1.0,
            "avg_amarelos": m("cartoes_amarelos"),
            "avg_escanteios": m("escanteios"),
            "over35_corners_pct": m("escanteios"),
        }

    home = extrair_medias(home_rows)
    away = extrair_medias(away_rows)

    if not home or not away:
        return {
            "status": "erro",
            "detalhe": "Dados insuficientes para rodar o modelo. "
                       "Pelo menos uma das seleções não tem estatísticas.",
        }

    resultado = rodar_modelo_completo(
        home_avg_gols_marcados=home.get("avg_gols_marcados", 1.0),
        home_avg_gols_sofridos=home.get("avg_gols_sofridos", 1.0),
        away_avg_gols_marcados=away.get("avg_gols_marcados", 1.0),
        away_avg_gols_sofridos=away.get("avg_gols_sofridos", 1.0),
        home_avg_amarelos=home.get("avg_amarelos"),
        away_avg_amarelos=away.get("avg_amarelos"),
        home_avg_escanteios=home.get("avg_escanteios"),
        away_avg_escanteios=away.get("avg_escanteios"),
        home_over35_corners_pct=home.get("over35_corners_pct"),
        away_over35_corners_pct=away.get("over35_corners_pct"),
    )

    return {"status": "ok", **resultado}

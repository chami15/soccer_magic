"""
Resolver — estatísticas agregadas de uma seleção (equivalente a team_stats),
calculadas a partir de fato_estatistica_selecao_partida + fato_partida via pandas.

Janela: até 5 jogos mais recentes, priorizando jogos de Copa; amistosos
preenchem as vagas restantes. data_quality: 'insufficient' (<3), 'partial'
(3-4), 'complete' (5).
"""

import pandas as pd

from utils.query_executor import executar_query

JANELA_MAXIMA = 5
COLUNAS_MEDIA = {
    "avg_goals_scored": "gols_marcados",
    "avg_goals_conceded": "gols_sofridos",
    "avg_corners": "escanteios",
    "avg_yellow_cards": "cartoes_amarelos",
    "avg_red_cards": "cartoes_vermelhos",
    "avg_shots_on_goal": "chutes_no_gol",
    "avg_possession": "posse_bola",
    "avg_goals_1h": "gols_1_tempo",
    "avg_goals_2h": "gols_2_tempo",
    "avg_shots_total": "chutes_total",
    "avg_shots_inside_box": "chutes_dentro_area",
    "avg_shots_outside_box": "chutes_fora_area",
    "avg_blocked_shots": "chutes_bloqueados",
    "avg_passes_total": "passes_total",
    "avg_passes_accurate": "passes_certos",
    "avg_offsides": "impedimentos",
    "avg_fouls": "faltas",
    "avg_saves": "defesas",
}


def _build_window(df: pd.DataFrame) -> pd.DataFrame:
    """Seleciona até JANELA_MAXIMA jogos, priorizando Copa sobre Amistoso, mais recentes primeiro."""
    df = df.sort_values("data_partida", ascending=False)
    copa = df[df["tipo"] == "Copa"]
    amistoso = df[df["tipo"] != "Copa"]
    faltam = JANELA_MAXIMA - len(copa)
    if faltam > 0:
        janela = pd.concat([copa, amistoso.head(faltam)])
    else:
        janela = copa.head(JANELA_MAXIMA)
    return janela.sort_values("data_partida", ascending=False)


def _data_quality(n: int) -> str:
    if n < 3:
        return "insufficient"
    if n < JANELA_MAXIMA:
        return "partial"
    return "complete"


def _form_sequence(janela: pd.DataFrame) -> str | None:
    if janela.empty:
        return None
    mapa = {"V": "V", "E": "E", "D": "D"}
    return " ".join(mapa.get(r, r) for r in janela["resultado"].tolist())


def _trend_goals_3v5(janela: pd.DataFrame) -> float | None:
    n = len(janela)
    if n == 0:
        return None
    media_total = janela["gols_marcados"].mean()
    media_3 = janela.head(3)["gols_marcados"].mean()
    return round(float(media_3 - media_total), 2)


def resolver_estatisticas_selecao(selecao_id: int) -> dict:
    """Calcula as estatísticas agregadas (formato team_stats) de uma seleção."""
    rows = executar_query("estatistica:select_by_selecao", params=(selecao_id,))

    if not rows:
        return {
            "team_id": selecao_id,
            "data_quality": "insufficient",
            "copa_count": 0,
            "friendly_count": 0,
            "form_sequence": None,
            "goal_distribution_summary": None,
            "tournament_overall_stats": None,
            **{campo: None for campo in COLUNAS_MEDIA},
            "over15_pct": None,
            "over25_pct": None,
            "over35_pct": None,
            "btts_pct": None,
            "clean_sheets": None,
            "over35_corners_pct": None,
            "avg_passes_pct": None,
            "trend_goals_3v5": None,
        }

    df = pd.DataFrame(rows)
    janela = _build_window(df)
    n = len(janela)

    resultado: dict = {
        "team_id": selecao_id,
        "data_quality": _data_quality(n),
        "copa_count": int((janela["tipo"] == "Copa").sum()),
        "friendly_count": int((janela["tipo"] != "Copa").sum()),
        "form_sequence": _form_sequence(janela),
        "goal_distribution_summary": None,
        "tournament_overall_stats": None,
    }

    if n == 0:
        for campo in COLUNAS_MEDIA:
            resultado[campo] = None
        resultado["over15_pct"] = None
        resultado["over25_pct"] = None
        resultado["over35_pct"] = None
        resultado["btts_pct"] = None
        resultado["clean_sheets"] = None
        resultado["over35_corners_pct"] = None
        resultado["avg_passes_pct"] = None
        resultado["trend_goals_3v5"] = None
        return resultado

    for campo, coluna in COLUNAS_MEDIA.items():
        resultado[campo] = round(float(janela[coluna].mean()), 2) if coluna in janela else None

    total_gols = janela["gols_marcados"] + janela["gols_sofridos"]
    resultado["over15_pct"] = round(float((total_gols >= 2).mean() * 100), 2)
    resultado["over25_pct"] = round(float((total_gols >= 3).mean() * 100), 2)
    resultado["over35_pct"] = round(float((total_gols >= 4).mean() * 100), 2)
    resultado["btts_pct"] = round(
        float(((janela["gols_marcados"] > 0) & (janela["gols_sofridos"] > 0)).mean() * 100), 2
    )
    resultado["clean_sheets"] = int((janela["gols_sofridos"] == 0).sum())
    resultado["over35_corners_pct"] = round(float((janela["escanteios"] >= 4).mean() * 100), 2)

    passes_pct_por_jogo = janela.apply(
        lambda linha: (linha["passes_certos"] / linha["passes_total"] * 100)
        if linha.get("passes_total")
        else None,
        axis=1,
    ).dropna()
    resultado["avg_passes_pct"] = (
        round(float(passes_pct_por_jogo.mean()), 2) if not passes_pct_por_jogo.empty else None
    )

    resultado["trend_goals_3v5"] = _trend_goals_3v5(janela)

    return resultado

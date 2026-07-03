"""
Modelos estatísticos puros — sem acesso a banco nem LLM.

Usa distribuição de Poisson para prever placares e calcular
probabilidades de mercados (1X2, over/under, BTTS, etc.).
"""

import math
from typing import Optional

# Médias de referência da Copa do Mundo (base histórica)
MEDIA_GOLS_COPA_HOME = 1.35
MEDIA_GOLS_COPA_AWAY = 1.02
MEDIA_ESCANTEIOS = 10.0
MEDIA_AMARELOS = 3.5

# Placar máximo simulado no modelo Poisson
MAX_GOLS = 8


def _poisson_pmf(k: int, lam: float) -> float:
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.exp(-lam) * (lam**k)) / math.factorial(k)


def _matriz_placar(lam_home: float, lam_away: float) -> list[list[float]]:
    """Matriz de probabilidades [gols_home][gols_away]."""
    return [
        [_poisson_pmf(h, lam_home) * _poisson_pmf(a, lam_away) for a in range(MAX_GOLS + 1)]
        for h in range(MAX_GOLS + 1)
    ]


def calcular_lambdas(
    home_avg_gols_marcados: float,
    home_avg_gols_sofridos: float,
    away_avg_gols_marcados: float,
    away_avg_gols_sofridos: float,
) -> tuple[float, float]:
    """
    Dixon-Coles simplificado: força de ataque e defesa relativas à média da Copa.
    Retorna (λ_home, λ_away).
    """
    ataque_home = max(home_avg_gols_marcados / MEDIA_GOLS_COPA_HOME, 0.1)
    defesa_home = max(home_avg_gols_sofridos / MEDIA_GOLS_COPA_AWAY, 0.1)
    ataque_away = max(away_avg_gols_marcados / MEDIA_GOLS_COPA_AWAY, 0.1)
    defesa_away = max(away_avg_gols_sofridos / MEDIA_GOLS_COPA_HOME, 0.1)

    lam_home = ataque_home * defesa_away * MEDIA_GOLS_COPA_HOME
    lam_away = ataque_away * defesa_home * MEDIA_GOLS_COPA_AWAY

    return round(lam_home, 4), round(lam_away, 4)


def calcular_probabilidades_1x2(matriz: list[list[float]]) -> dict:
    prob_home = sum(
        matriz[h][a] for h in range(MAX_GOLS + 1) for a in range(MAX_GOLS + 1) if h > a
    )
    prob_empate = sum(
        matriz[h][a] for h in range(MAX_GOLS + 1) for a in range(MAX_GOLS + 1) if h == a
    )
    prob_away = 1.0 - prob_home - prob_empate
    return {
        "home": round(prob_home * 100, 2),
        "empate": round(prob_empate * 100, 2),
        "away": round(max(prob_away, 0.0) * 100, 2),
    }


def calcular_over_under(matriz: list[list[float]]) -> dict:
    resultados = {}
    for linha in [1.5, 2.5, 3.5, 4.5]:
        total_int = int(linha + 0.5)
        prob_over = sum(
            matriz[h][a]
            for h in range(MAX_GOLS + 1)
            for a in range(MAX_GOLS + 1)
            if h + a >= total_int
        )
        resultados[f"over_{linha}"] = round(prob_over * 100, 2)
        resultados[f"under_{linha}"] = round((1.0 - prob_over) * 100, 2)
    return resultados


def calcular_btts(lam_home: float, lam_away: float) -> dict:
    prob_home_marca = 1 - _poisson_pmf(0, lam_home)
    prob_away_marca = 1 - _poisson_pmf(0, lam_away)
    btts = prob_home_marca * prob_away_marca
    return {
        "btts_sim": round(btts * 100, 2),
        "btts_nao": round((1 - btts) * 100, 2),
    }


def calcular_placar_mais_provavel(matriz: list[list[float]]) -> dict:
    melhor_prob = 0.0
    melhor = (0, 0)
    top3 = []
    for h in range(MAX_GOLS + 1):
        for a in range(MAX_GOLS + 1):
            prob = matriz[h][a]
            top3.append((prob, h, a))
            if prob > melhor_prob:
                melhor_prob = prob
                melhor = (h, a)
    top3.sort(reverse=True)
    return {
        "placar": f"{melhor[0]}-{melhor[1]}",
        "probabilidade": round(melhor_prob * 100, 2),
        "top3": [
            {"placar": f"{h}-{a}", "probabilidade": round(p * 100, 2)}
            for p, h, a in top3[:3]
        ],
    }


def calcular_mercado_amarelos(
    home_avg: Optional[float],
    away_avg: Optional[float],
) -> dict:
    if home_avg is None or away_avg is None:
        return {"total_esperado": None, "over_3_5": None, "over_4_5": None}
    total = home_avg + away_avg
    over_3_5 = min(round((total / MEDIA_AMARELOS) * 55, 2), 95.0)
    over_4_5 = min(round((total / MEDIA_AMARELOS) * 35, 2), 90.0)
    return {
        "total_esperado": round(total, 2),
        "over_3_5": over_3_5,
        "over_4_5": over_4_5,
    }


def calcular_mercado_escanteios(
    home_avg: Optional[float],
    away_avg: Optional[float],
    home_over35_pct: Optional[float],
    away_over35_pct: Optional[float],
) -> dict:
    if home_avg is None or away_avg is None:
        return {"total_esperado": None, "over_9_5": None, "over_10_5": None}
    total = home_avg + away_avg
    over_9_5 = round(min((total / MEDIA_ESCANTEIOS) * 55, 95.0), 2)
    over_10_5 = round(min((total / MEDIA_ESCANTEIOS) * 42, 90.0), 2)
    if home_over35_pct and away_over35_pct:
        ajuste = ((home_over35_pct + away_over35_pct) / 2) / 100
        over_9_5 = round(min(over_9_5 * (0.8 + 0.4 * ajuste), 95.0), 2)
    return {
        "total_esperado": round(total, 2),
        "over_9_5": over_9_5,
        "over_10_5": over_10_5,
    }


def rodar_modelo_completo(
    home_avg_gols_marcados: float,
    home_avg_gols_sofridos: float,
    away_avg_gols_marcados: float,
    away_avg_gols_sofridos: float,
    home_avg_amarelos: Optional[float] = None,
    away_avg_amarelos: Optional[float] = None,
    home_avg_escanteios: Optional[float] = None,
    away_avg_escanteios: Optional[float] = None,
    home_over35_corners_pct: Optional[float] = None,
    away_over35_corners_pct: Optional[float] = None,
) -> dict:
    """Ponto de entrada único: roda todos os mercados e retorna dict completo."""
    lam_home, lam_away = calcular_lambdas(
        home_avg_gols_marcados,
        home_avg_gols_sofridos,
        away_avg_gols_marcados,
        away_avg_gols_sofridos,
    )
    matriz = _matriz_placar(lam_home, lam_away)

    return {
        "lambda_home": lam_home,
        "lambda_away": lam_away,
        "placar_mais_provavel": calcular_placar_mais_provavel(matriz),
        "resultado_1x2": calcular_probabilidades_1x2(matriz),
        "over_under": calcular_over_under(matriz),
        "btts": calcular_btts(lam_home, lam_away),
        "amarelos": calcular_mercado_amarelos(home_avg_amarelos, away_avg_amarelos),
        "escanteios": calcular_mercado_escanteios(
            home_avg_escanteios,
            away_avg_escanteios,
            home_over35_corners_pct,
            away_over35_corners_pct,
        ),
    }

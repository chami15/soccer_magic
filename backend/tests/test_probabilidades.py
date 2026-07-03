"""
Testes unitários — agente/probabilidades.py

Cobre: calcular_lambdas, 1X2, over/under, BTTS, placar mais provável,
amarelos, escanteios e rodar_modelo_completo.
"""
import math
import pytest
from agente.probabilidades import (
    MEDIA_GOLS_COPA_HOME,
    MEDIA_GOLS_COPA_AWAY,
    MAX_GOLS,
    _poisson_pmf,
    _matriz_placar,
    calcular_lambdas,
    calcular_probabilidades_1x2,
    calcular_over_under,
    calcular_btts,
    calcular_placar_mais_provavel,
    calcular_mercado_amarelos,
    calcular_mercado_escanteios,
    rodar_modelo_completo,
)


# ── _poisson_pmf ──────────────────────────────────────────────────────────────

def test_poisson_pmf_zero_gols():
    # P(0; λ=1.5) = e^-1.5 ≈ 0.2231
    result = _poisson_pmf(0, 1.5)
    assert abs(result - math.exp(-1.5)) < 1e-9


def test_poisson_pmf_lambda_zero():
    assert _poisson_pmf(0, 0) == 1.0
    assert _poisson_pmf(1, 0) == 0.0


def test_poisson_pmf_valores_positivos():
    for k in range(5):
        assert _poisson_pmf(k, 1.2) >= 0


# ── _matriz_placar ─────────────────────────────────────────────────────────────

def test_matriz_soma_proxima_de_1():
    m = _matriz_placar(1.35, 1.02)
    total = sum(m[h][a] for h in range(MAX_GOLS + 1) for a in range(MAX_GOLS + 1))
    assert abs(total - 1.0) < 0.01


def test_matriz_dimensoes():
    m = _matriz_placar(1.0, 1.0)
    assert len(m) == MAX_GOLS + 1
    assert all(len(row) == MAX_GOLS + 1 for row in m)


# ── calcular_lambdas ──────────────────────────────────────────────────────────

def test_lambdas_time_mediano():
    # Time com médias iguais à média da Copa → λ deve ser exatamente a média
    lam_h, lam_a = calcular_lambdas(
        MEDIA_GOLS_COPA_HOME, MEDIA_GOLS_COPA_AWAY,
        MEDIA_GOLS_COPA_AWAY, MEDIA_GOLS_COPA_HOME,
    )
    assert abs(lam_h - MEDIA_GOLS_COPA_HOME) < 0.01
    assert abs(lam_a - MEDIA_GOLS_COPA_AWAY) < 0.01


def test_lambdas_minimo_positivo():
    # Times sem gols marcados → piso de 0.1 aplicado
    lam_h, lam_a = calcular_lambdas(0.0, 0.0, 0.0, 0.0)
    assert lam_h > 0
    assert lam_a > 0


def test_lambdas_ataque_forte():
    # Time home com ataque forte marca mais do que a média
    lam_h, lam_a = calcular_lambdas(3.0, 0.5, 1.0, 1.0)
    assert lam_h > MEDIA_GOLS_COPA_HOME


def test_lambdas_retorna_arredondado():
    lam_h, lam_a = calcular_lambdas(1.5, 0.8, 1.2, 1.0)
    assert lam_h == round(lam_h, 4)
    assert lam_a == round(lam_a, 4)


# ── calcular_probabilidades_1x2 ───────────────────────────────────────────────

def test_1x2_soma_100():
    m = _matriz_placar(1.35, 1.02)
    r = calcular_probabilidades_1x2(m)
    total = r["home"] + r["empate"] + r["away"]
    assert abs(total - 100.0) < 0.1


def test_1x2_home_favorito_tem_maior_prob():
    # λ home muito alto → home deve ter probabilidade maior
    m = _matriz_placar(3.0, 0.5)
    r = calcular_probabilidades_1x2(m)
    assert r["home"] > r["away"]
    assert r["home"] > r["empate"]


def test_1x2_sem_valores_negativos():
    m = _matriz_placar(0.5, 3.0)
    r = calcular_probabilidades_1x2(m)
    assert r["home"] >= 0
    assert r["empate"] >= 0
    assert r["away"] >= 0


# ── calcular_over_under ───────────────────────────────────────────────────────

def test_over_under_chaves_presentes():
    m = _matriz_placar(1.35, 1.02)
    r = calcular_over_under(m)
    for linha in [1.5, 2.5, 3.5, 4.5]:
        assert f"over_{linha}" in r
        assert f"under_{linha}" in r


def test_over_under_soma_100():
    m = _matriz_placar(1.35, 1.02)
    r = calcular_over_under(m)
    for linha in [1.5, 2.5, 3.5, 4.5]:
        total = r[f"over_{linha}"] + r[f"under_{linha}"]
        assert abs(total - 100.0) < 0.2, f"Linha {linha}: {total}"


def test_over_15_maior_que_over_25():
    m = _matriz_placar(1.35, 1.02)
    r = calcular_over_under(m)
    assert r["over_1.5"] > r["over_2.5"] > r["over_3.5"] > r["over_4.5"]


# ── calcular_btts ─────────────────────────────────────────────────────────────

def test_btts_soma_100():
    r = calcular_btts(1.35, 1.02)
    assert abs(r["btts_sim"] + r["btts_nao"] - 100.0) < 0.1


def test_btts_lambdas_altos_mais_provavel():
    r_alto = calcular_btts(3.0, 3.0)
    r_baixo = calcular_btts(0.3, 0.3)
    assert r_alto["btts_sim"] > r_baixo["btts_sim"]


# ── calcular_placar_mais_provavel ─────────────────────────────────────────────

def test_placar_mais_provavel_formato():
    m = _matriz_placar(1.35, 1.02)
    r = calcular_placar_mais_provavel(m)
    assert "placar" in r
    assert "probabilidade" in r
    assert "top3" in r
    assert len(r["top3"]) == 3


def test_placar_mais_provavel_0_0_com_lambdas_baixos():
    m = _matriz_placar(0.1, 0.1)
    r = calcular_placar_mais_provavel(m)
    assert r["placar"] == "0-0"


def test_top3_ordenado_por_probabilidade():
    m = _matriz_placar(1.35, 1.02)
    r = calcular_placar_mais_provavel(m)
    probs = [p["probabilidade"] for p in r["top3"]]
    assert probs == sorted(probs, reverse=True)


# ── calcular_mercado_amarelos ─────────────────────────────────────────────────

def test_amarelos_com_valores():
    r = calcular_mercado_amarelos(2.0, 2.0)
    assert r["total_esperado"] == 4.0
    assert r["over_3_5"] is not None
    assert r["over_4_5"] is not None
    assert 0 <= r["over_3_5"] <= 95
    assert 0 <= r["over_4_5"] <= 90


def test_amarelos_sem_valores():
    r = calcular_mercado_amarelos(None, None)
    assert r["total_esperado"] is None
    assert r["over_3_5"] is None


def test_amarelos_cap_maximo():
    # Valores muito altos → capped em 95 e 90
    r = calcular_mercado_amarelos(100.0, 100.0)
    assert r["over_3_5"] <= 95.0
    assert r["over_4_5"] <= 90.0


# ── calcular_mercado_escanteios ───────────────────────────────────────────────

def test_escanteios_com_valores():
    r = calcular_mercado_escanteios(5.0, 5.0, None, None)
    assert r["total_esperado"] == 10.0
    assert r["over_9_5"] is not None
    assert r["over_10_5"] is not None


def test_escanteios_sem_valores():
    r = calcular_mercado_escanteios(None, None, None, None)
    assert r["total_esperado"] is None


def test_escanteios_cap_maximo():
    r = calcular_mercado_escanteios(100.0, 100.0, None, None)
    assert r["over_9_5"] <= 95.0
    assert r["over_10_5"] <= 90.0


# ── rodar_modelo_completo ─────────────────────────────────────────────────────

def test_rodar_modelo_completo_chaves():
    r = rodar_modelo_completo(
        home_avg_gols_marcados=1.6,
        home_avg_gols_sofridos=0.8,
        away_avg_gols_marcados=1.2,
        away_avg_gols_sofridos=1.0,
    )
    for chave in ["lambda_home", "lambda_away", "placar_mais_provavel",
                  "resultado_1x2", "over_under", "btts", "amarelos", "escanteios"]:
        assert chave in r, f"Chave '{chave}' ausente"


def test_rodar_modelo_completo_lambdas_positivos():
    r = rodar_modelo_completo(1.5, 1.0, 1.2, 0.9)
    assert r["lambda_home"] > 0
    assert r["lambda_away"] > 0


def test_rodar_modelo_completo_com_extras():
    r = rodar_modelo_completo(
        home_avg_gols_marcados=1.8,
        home_avg_gols_sofridos=0.6,
        away_avg_gols_marcados=1.0,
        away_avg_gols_sofridos=1.2,
        home_avg_amarelos=2.0,
        away_avg_amarelos=1.5,
        home_avg_escanteios=5.5,
        away_avg_escanteios=4.0,
        home_over35_corners_pct=60.0,
        away_over35_corners_pct=40.0,
    )
    assert r["amarelos"]["total_esperado"] == 3.5
    assert r["escanteios"]["total_esperado"] == 9.5

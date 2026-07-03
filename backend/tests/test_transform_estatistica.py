"""
Testes unitários — pipeline/transformers/estatistica.py
"""
import pytest
from tests.conftest import make_match, make_stats_groups
from pipeline.transformers.estatistica import transform_estatistica, _num, _passes_precisao_pct


# ── _num: extração de valor numérico ─────────────────────────────────────────

def test_num_via_homeValue():
    item = {"homeValue": 60, "awayValue": 40}
    assert _num(item, "home") == 60


def test_num_via_campo_bruto_string():
    item = {"home": "60%", "away": "40%"}
    assert _num(item, "home") == 60.0


def test_num_campo_bruto_float_string():
    item = {"home": "7.5"}
    assert _num(item, "home") == 7.5


def test_num_none_quando_item_none():
    assert _num(None, "home") is None


def test_num_none_quando_sem_valor():
    item = {"key": "passes"}
    assert _num(item, "home") is None


# ── _passes_precisao_pct ──────────────────────────────────────────────────────

def test_passes_precisao_pct_calculo():
    flat = {
        "passes": {"homeValue": 400},
        "accuratePasses": {"homeValue": 360},
    }
    result = _passes_precisao_pct(flat, "home")
    assert result == 90.0


def test_passes_precisao_pct_zero_total():
    flat = {
        "passes": {"homeValue": 0},
        "accuratePasses": {"homeValue": 0},
    }
    assert _passes_precisao_pct(flat, "home") is None


def test_passes_precisao_pct_sem_chave():
    flat = {}
    assert _passes_precisao_pct(flat, "home") is None


# ── transform_estatistica: resultado ─────────────────────────────────────────

def test_resultado_vitoria_home():
    m = make_match(home_id=10, away_id=20, home_goals=2, away_goals=0)
    home, away = transform_estatistica([], m)
    assert home["resultado"] == "V"
    assert away["resultado"] == "D"


def test_resultado_vitoria_away():
    m = make_match(home_id=10, away_id=20, home_goals=0, away_goals=3)
    home, away = transform_estatistica([], m)
    assert home["resultado"] == "D"
    assert away["resultado"] == "V"


def test_resultado_empate():
    m = make_match(home_id=10, away_id=20, home_goals=1, away_goals=1)
    home, away = transform_estatistica([], m)
    assert home["resultado"] == "E"
    assert away["resultado"] == "E"


# ── transform_estatistica: gols ───────────────────────────────────────────────

def test_gols_marcados_e_sofridos():
    m = make_match(home_id=10, away_id=20, home_goals=3, away_goals=1)
    home, away = transform_estatistica([], m)
    assert home["gols_marcados"] == 3
    assert home["gols_sofridos"] == 1
    assert away["gols_marcados"] == 1
    assert away["gols_sofridos"] == 3


def test_gols_2_tempo_calculado():
    m = make_match(home_goals=3, away_goals=2, ht_home=1, ht_away=1)
    home, away = transform_estatistica([], m)
    assert home["gols_2_tempo"] == 2   # 3 - 1
    assert away["gols_2_tempo"] == 1   # 2 - 1


def test_gols_1_tempo():
    m = make_match(home_goals=3, away_goals=2, ht_home=2, ht_away=0)
    home, away = transform_estatistica([], m)
    assert home["gols_1_tempo"] == 2
    assert away["gols_1_tempo"] == 0


# ── transform_estatistica: selecao_id e partida_id ───────────────────────────

def test_ids_corretos():
    m = make_match(match_id=99, home_id=10, away_id=20)
    home, away = transform_estatistica([], m)
    assert home["partida_id"] == 99
    assert home["selecao_id"] == 10
    assert away["partida_id"] == 99
    assert away["selecao_id"] == 20


# ── transform_estatistica: estatísticas do payload ───────────────────────────

def test_estatisticas_extraidas():
    m = make_match(home_id=10, away_id=20, home_goals=1, away_goals=0)
    groups = make_stats_groups(
        posse_home=60,
        chutes_home=10,
        escanteios_home=5,
        passes_home=400,
        passes_certos_home=360,
        cartao_amarelo_home=1,
        posse_away=40,
        chutes_away=4,
        escanteios_away=2,
        passes_away=280,
        passes_certos_away=220,
        cartao_amarelo_away=2,
    )
    home, away = transform_estatistica(groups, m)

    assert home["posse_bola"] == 60
    assert home["chutes_total"] == 10
    assert home["escanteios"] == 5
    assert home["passes_total"] == 400
    assert home["passes_certos"] == 360
    assert home["passes_precisao_pct"] == 90.0
    assert home["cartoes_amarelos"] == 1

    assert away["posse_bola"] == 40
    assert away["chutes_total"] == 4
    assert away["escanteios"] == 2
    assert away["passes_precisao_pct"] == round(220 / 280 * 100, 2)
    assert away["cartoes_amarelos"] == 2


def test_estatisticas_vazio_sem_erro():
    m = make_match()
    home, away = transform_estatistica([], m)
    assert home["posse_bola"] is None
    assert home["chutes_total"] is None
    assert home["passes_precisao_pct"] is None


# ── transform_estatistica: performance points ────────────────────────────────

def test_performance_rating_home():
    m = make_match(home_id=10, away_id=20)
    home, away = transform_estatistica([], m, performance_points={10: 7.8, 20: 6.5})
    assert home["performance_rating"] == 7.8
    assert away["performance_rating"] == 6.5


def test_performance_rating_ausente():
    m = make_match(home_id=10, away_id=20)
    home, away = transform_estatistica([], m, performance_points={})
    assert home["performance_rating"] is None
    assert away["performance_rating"] is None

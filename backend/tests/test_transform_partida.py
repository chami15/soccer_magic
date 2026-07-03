"""
Testes unitários — pipeline/transformers/partida.py
"""
import pytest
from tests.conftest import make_match, WC_TOURNAMENT_ID
from pipeline.transformers.partida import transform_partida

FRIENDLY_ID = 999


# ── Campos básicos ─────────────────────────────────────────────────────────────

def test_campos_basicos():
    m = make_match(match_id=42, home_id=10, away_id=20, home_goals=2, away_goals=1)
    r = transform_partida(m)
    assert r["id"] == 42
    assert r["selecao_home_id"] == 10
    assert r["selecao_away_id"] == 20
    assert r["placar_home"] == 2
    assert r["placar_away"] == 1
    assert r["status"] == "finished"
    assert r["custom_id"] == "abc123"


# ── Vencedor ──────────────────────────────────────────────────────────────────

def test_vencedor_home():
    m = make_match(home_id=10, away_id=20, home_goals=3, away_goals=0)
    assert transform_partida(m)["vencedor_id"] == 10


def test_vencedor_away():
    m = make_match(home_id=10, away_id=20, home_goals=0, away_goals=2)
    assert transform_partida(m)["vencedor_id"] == 20


def test_vencedor_empate_none():
    m = make_match(home_id=10, away_id=20, home_goals=1, away_goals=1)
    assert transform_partida(m)["vencedor_id"] is None


def test_vencedor_none_quando_nao_finalizado():
    m = make_match(home_goals=2, away_goals=0, status="inprogress")
    assert transform_partida(m)["vencedor_id"] is None


# ── Tipo Copa / Amistoso ──────────────────────────────────────────────────────

def test_tipo_copa():
    m = make_match(tournament_id=WC_TOURNAMENT_ID)
    assert transform_partida(m)["tipo"] == "Copa"


def test_tipo_amistoso():
    m = make_match(tournament_id=FRIENDLY_ID)
    assert transform_partida(m)["tipo"] == "Amistoso"


# ── Placar no intervalo ───────────────────────────────────────────────────────

def test_placar_ht():
    m = make_match(home_goals=3, away_goals=2, ht_home=1, ht_away=1)
    r = transform_partida(m)
    assert r["placar_ht_home"] == 1
    assert r["placar_ht_away"] == 1


# ── Data da partida ───────────────────────────────────────────────────────────

def test_data_partida_formato_iso():
    # timestamp 0 = 1970-01-01
    m = make_match(timestamp=0)
    assert transform_partida(m)["data_partida"] == "1970-01-01"


def test_data_partida_timestamp_moderno():
    # 2024-06-14 00:00:00 UTC
    m = make_match(timestamp=1718323200)
    assert transform_partida(m)["data_partida"] == "2024-06-14"


# ── Metadados opcionais ───────────────────────────────────────────────────────

def test_grupo_e_rodada():
    m = make_match(group_name="Group B", round_num=3)
    r = transform_partida(m)
    assert r["grupo"] == "Group B"
    assert r["rodada"] == 3


def test_cidade():
    m = make_match(city="São Paulo")
    assert transform_partida(m)["cidade"] == "São Paulo"


def test_custom_id_none():
    m = make_match()
    m["customId"] = None
    assert transform_partida(m)["custom_id"] is None


# ── Partida futura (sem placar) ───────────────────────────────────────────────

def test_partida_futura_sem_placar():
    m = make_match(status="notstarted")
    m["homeScore"] = {"current": None}
    m["awayScore"] = {"current": None}
    r = transform_partida(m)
    assert r["placar_home"] is None
    assert r["placar_away"] is None
    assert r["vencedor_id"] is None

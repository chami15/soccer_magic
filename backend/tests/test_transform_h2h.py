"""
Testes unitários — pipeline/transformers/h2h.py
"""
from pipeline.transformers.h2h import _score, transform_h2h, extrair_adversarios

SELECAO_A = 10
SELECAO_B = 20


# ── _score: extração robusta de placar ────────────────────────────────────────

def test_score_via_current():
    assert _score({"current": 2}) == 2

def test_score_via_display():
    assert _score({"display": "3"}) == 3

def test_score_via_periodos():
    assert _score({"period1": 1, "period2": 2}) == 3

def test_score_via_periodos_com_prorrogacao():
    assert _score({"period1": 1, "period2": 1, "overtime": 1}) == 3

def test_score_none_quando_vazio():
    assert _score({}) is None

def test_score_none_quando_none():
    assert _score(None) is None


def _event(
    event_id: int = 1,
    home_id: int = SELECAO_A,
    away_id: int = SELECAO_B,
    home_score: int = 2,
    away_score: int = 1,
    winner_code: int | None = 1,
    timestamp: int = 1700000000,
    torneio: str = "FIFA World Cup",
) -> dict:
    return {
        "id": event_id,
        "homeTeam": {"id": home_id, "name": "Home FC"},
        "awayTeam": {"id": away_id, "name": "Away FC"},
        "homeScore": {"current": home_score},
        "awayScore": {"current": away_score},
        "winnerCode": winner_code,
        "startTimestamp": timestamp,
        "tournament": {"name": torneio},
    }


# ── Perspectiva quando selecao_a é home ──────────────────────────────────────

def test_selecao_a_home_placar():
    r = transform_h2h(_event(home_id=SELECAO_A, away_id=SELECAO_B, home_score=3, away_score=0), SELECAO_A)
    assert r["selecao_a_id"] == SELECAO_A
    assert r["selecao_b_id"] == SELECAO_B
    assert r["placar_a"] == 3
    assert r["placar_b"] == 0


def test_selecao_a_away_placar():
    r = transform_h2h(_event(home_id=SELECAO_B, away_id=SELECAO_A, home_score=1, away_score=2), SELECAO_A)
    assert r["placar_a"] == 2
    assert r["placar_b"] == 1


# ── Vencedor via winnerCode ───────────────────────────────────────────────────

def test_vencedor_home_winner_code_1():
    r = transform_h2h(_event(home_id=SELECAO_A, winner_code=1), SELECAO_A)
    assert r["vencedor_id"] == SELECAO_A


def test_vencedor_away_winner_code_2():
    r = transform_h2h(_event(home_id=SELECAO_A, away_id=SELECAO_B, winner_code=2), SELECAO_A)
    assert r["vencedor_id"] == SELECAO_B


def test_vencedor_none_sem_winner_code():
    r = transform_h2h(_event(winner_code=None), SELECAO_A)
    assert r["vencedor_id"] is None


# ── Data da partida ───────────────────────────────────────────────────────────

def test_data_partida_iso():
    # 2023-11-15 00:00:00 UTC
    r = transform_h2h(_event(timestamp=1700006400), SELECAO_A)
    assert r["data_partida"] == "2023-11-15"


def test_data_partida_none_sem_timestamp():
    e = _event()
    del e["startTimestamp"]
    r = transform_h2h(e, SELECAO_A)
    assert r["data_partida"] is None


# ── Performance sempre None ───────────────────────────────────────────────────

def test_performance_sempre_none():
    r = transform_h2h(_event(), SELECAO_A)
    assert r["performance_a"] is None
    assert r["performance_b"] is None


# ── extrair_adversarios ───────────────────────────────────────────────────────

def test_extrair_adversarios_home():
    events = [
        _event(event_id=1, home_id=SELECAO_A, away_id=SELECAO_B),
        _event(event_id=2, home_id=SELECAO_A, away_id=99),
    ]
    advs = extrair_adversarios(events, SELECAO_A)
    ids = [a["id"] for a in advs]
    assert SELECAO_B in ids
    assert 99 in ids
    assert SELECAO_A not in ids


def test_extrair_adversarios_sem_duplicatas():
    events = [
        _event(event_id=1, home_id=SELECAO_A, away_id=SELECAO_B),
        _event(event_id=2, home_id=SELECAO_B, away_id=SELECAO_A),
    ]
    advs = extrair_adversarios(events, SELECAO_A)
    assert len(advs) == 1
    assert advs[0]["id"] == SELECAO_B


def test_extrair_adversarios_lista_vazia():
    assert extrair_adversarios([], SELECAO_A) == []

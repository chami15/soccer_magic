"""
Tests for window.py — 100% coverage of the 7 scenarios from §7.3 SPECv2.
Uses Sofascore event data format (SPECv2).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from window import build_window, WC_TOURNAMENT_ID

FRIENDLY_TOURNAMENT_ID = 999  # qualquer ID != WC para amistoso


def copa(match_id: int, timestamp: int) -> dict:
    """Evento Copa no formato Sofascore."""
    return {
        "id": match_id,
        "startTimestamp": timestamp,
        "tournament": {"uniqueTournament": {"id": WC_TOURNAMENT_ID}},
        "homeTeam": {"id": 999, "name": "Home"},
        "awayTeam": {"id": 888, "name": "Away"},
        "homeScore": {"current": 1, "period1": 0},
        "awayScore": {"current": 0, "period1": 0},
        "status": {"type": "finished"},
    }


def friendly(match_id: int, timestamp: int) -> dict:
    """Evento amistoso no formato Sofascore (tournament_id != WC)."""
    return {
        "id": match_id,
        "startTimestamp": timestamp,
        "tournament": {"uniqueTournament": {"id": FRIENDLY_TOURNAMENT_ID}},
        "homeTeam": {"id": 999, "name": "Home"},
        "awayTeam": {"id": 888, "name": "Away"},
        "homeScore": {"current": 1, "period1": 0},
        "awayScore": {"current": 0, "period1": 0},
        "status": {"type": "finished"},
    }


# --- Cenário 1: Início da Copa (1 Copa + N amistosos) ---
def test_scenario_1_inicio_copa():
    matches = [copa(1, 1000)] + [friendly(i + 10, 500 - i * 10) for i in range(6)]
    result = build_window(matches)
    assert result.copa_count == 1
    assert result.friendly_count == 4
    assert len(result.window) == 5
    assert result.data_quality == "complete"
    assert result.window[0]["id"] == 1  # Copa entra primeiro


# --- Cenário 2: Após 2ª rodada (2 Copa + N amistosos) ---
def test_scenario_2_segunda_rodada():
    matches = [copa(1, 2000), copa(2, 1800)] + [friendly(i + 10, 900 - i * 10) for i in range(5)]
    result = build_window(matches)
    assert result.copa_count == 2
    assert result.friendly_count == 3
    assert len(result.window) == 5
    assert result.data_quality == "complete"


# --- Cenário 3: Após 3ª rodada (3 Copa + N amistosos) ---
def test_scenario_3_terceira_rodada():
    matches = [copa(i + 1, 3000 - i * 200) for i in range(3)] + [
        friendly(i + 10, 500 - i * 10) for i in range(4)
    ]
    result = build_window(matches)
    assert result.copa_count == 3
    assert result.friendly_count == 2
    assert len(result.window) == 5
    assert result.data_quality == "complete"


# --- Cenário 4: Oitavas (4 Copa + N amistosos) ---
def test_scenario_4_oitavas():
    matches = [copa(i + 1, 4000 - i * 200) for i in range(4)] + [
        friendly(i + 10, 300 - i * 10) for i in range(3)
    ]
    result = build_window(matches)
    assert result.copa_count == 4
    assert result.friendly_count == 1
    assert len(result.window) == 5
    assert result.data_quality == "complete"


# --- Cenário 5: Quartas e além (5+ Copa → apenas Copa) ---
def test_scenario_5_quartas_apenas_copa():
    matches = [copa(i + 1, 5000 - i * 200) for i in range(7)] + [
        friendly(i + 10, 100 - i * 10) for i in range(3)
    ]
    result = build_window(matches)
    assert result.copa_count == 5
    assert result.friendly_count == 0
    assert len(result.window) == 5
    assert result.data_quality == "complete"


# --- Cenário 6: Rodada dupla (Copa ordenada por startTimestamp DESC) ---
def test_scenario_6_rodada_dupla():
    matches = [
        copa(10, 6000),   # mais recente
        copa(11, 5800),
        copa(1, 3000),    # mais antigo
        friendly(20, 2500),
        friendly(21, 2000),
    ]
    result = build_window(matches)
    assert result.copa_count == 3
    assert result.friendly_count == 2
    assert len(result.window) == 5
    copa_in_window = [m for m in result.window if m["tournament"]["uniqueTournament"]["id"] == WC_TOURNAMENT_ID]
    assert copa_in_window[0]["id"] == 10  # mais recente primeiro


# --- Cenário 7: Janela com apenas amistosos (pré-Copa) ---
def test_scenario_7_apenas_amistosos():
    matches = [friendly(i + 10, 1000 - i * 100) for i in range(6)]
    result = build_window(matches)
    assert result.copa_count == 0
    assert result.friendly_count == 5
    assert len(result.window) == 5
    assert result.data_quality == "complete"


# --- Cenário extra: Dados insuficientes (menos de 3 jogos) ---
def test_insufficient_data():
    matches = [friendly(1, 1000), friendly(2, 900)]
    result = build_window(matches)
    assert result.data_quality == "insufficient"
    assert len(result.window) == 2


# --- Cenário extra: Dados parciais (3 ou 4 jogos) ---
def test_partial_data_3_games():
    matches = [copa(1, 1000), friendly(10, 800), friendly(11, 700)]
    result = build_window(matches)
    assert result.data_quality == "partial"
    assert len(result.window) == 3


def test_partial_data_4_games():
    matches = [copa(1, 2000), copa(2, 1800), friendly(10, 900), friendly(11, 800)]
    result = build_window(matches)
    assert result.data_quality == "partial"
    assert len(result.window) == 4


# --- Cenário: Lista vazia ---
def test_empty_matches():
    result = build_window([])
    assert result.data_quality == "insufficient"
    assert len(result.window) == 0
    assert result.copa_count == 0
    assert result.friendly_count == 0


# --- Copa sempre entra antes dos amistosos, independente da ordem de entrada ---
def test_copa_priority_over_friendly():
    matches = [
        friendly(10, 900),
        friendly(11, 800),
        friendly(12, 700),
        copa(1, 500),     # Copa mais antiga mas entra primeiro na janela
        friendly(13, 600),
    ]
    result = build_window(matches)
    assert result.window[0]["id"] == 1  # Copa primeiro
    assert result.copa_count == 1
    assert result.friendly_count == 4


# --- Copa mais recente vem primeiro na janela ---
def test_copa_ordered_by_timestamp_desc():
    matches = [
        copa(1, 1000),
        copa(2, 3000),  # mais recente
        copa(3, 2000),
    ]
    result = build_window(matches)
    ids = [m["id"] for m in result.window]
    assert ids == [2, 3, 1]


# --- Amistosos também ordenados por timestamp DESC ---
def test_friendly_ordered_by_timestamp_desc():
    matches = [
        friendly(10, 1000),
        friendly(11, 3000),  # mais recente
        friendly(12, 2000),
        friendly(13, 500),
        friendly(14, 100),
    ]
    result = build_window(matches)
    ids = [m["id"] for m in result.window]
    assert ids == [11, 12, 10, 13, 14]


# --- wc_tournament_id customizado ---
def test_custom_tournament_id():
    custom_id = 42
    matches = [
        {
            "id": 1,
            "startTimestamp": 1000,
            "tournament": {"uniqueTournament": {"id": custom_id}},
            "homeTeam": {"id": 1}, "awayTeam": {"id": 2},
            "homeScore": {"current": 1}, "awayScore": {"current": 0},
        },
        {
            "id": 2,
            "startTimestamp": 900,
            "tournament": {"uniqueTournament": {"id": 99}},
            "homeTeam": {"id": 1}, "awayTeam": {"id": 2},
            "homeScore": {"current": 0}, "awayScore": {"current": 0},
        },
    ]
    result = build_window(matches, wc_tournament_id=custom_id)
    assert result.copa_count == 1
    assert result.friendly_count == 1
    assert result.window[0]["id"] == 1  # Copa primeiro

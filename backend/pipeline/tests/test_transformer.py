"""
Tests for transformer.py — core transformation logic (SPECv2 / Sofascore format).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from window import WindowResult, WC_TOURNAMENT_ID
from transformer import transform, get_team_goals_scored, get_team_goals_conceded, get_result

TEAM_ID = 10
FRIENDLY_ID = 999


def make_match(
    match_id: int,
    tournament_id: int,
    home_id: int,
    away_id: int,
    home_goals: int,
    away_goals: int,
    timestamp: int | None = None,
) -> dict:
    """Cria evento no formato Sofascore."""
    return {
        "id": match_id,
        "startTimestamp": timestamp if timestamp is not None else 1750000000 + match_id,
        "tournament": {"uniqueTournament": {"id": tournament_id}},
        "homeTeam": {"id": home_id, "name": "Home"},
        "awayTeam": {"id": away_id, "name": "Away"},
        "homeScore": {"current": home_goals},
        "awayScore": {"current": away_goals},
        "status": {"type": "finished"},
    }


def make_window(matches: list[dict]) -> WindowResult:
    from window import build_window
    return build_window(matches, wc_tournament_id=WC_TOURNAMENT_ID)


# ─── Helpers individuais ───────────────────────────────────────────────────────

def test_get_team_goals_scored_home():
    m = make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 3, 1)
    assert get_team_goals_scored(m, TEAM_ID) == 3


def test_get_team_goals_scored_away():
    m = make_match(1, WC_TOURNAMENT_ID, 999, TEAM_ID, 1, 2)
    assert get_team_goals_scored(m, TEAM_ID) == 2


def test_get_team_goals_conceded_home():
    m = make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 3, 1)
    assert get_team_goals_conceded(m, TEAM_ID) == 1


def test_get_team_goals_conceded_away():
    m = make_match(1, WC_TOURNAMENT_ID, 999, TEAM_ID, 2, 0)
    assert get_team_goals_conceded(m, TEAM_ID) == 2


def test_get_result_win():
    m = make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 2, 0)
    assert get_result(m, TEAM_ID) == "V"


def test_get_result_draw():
    m = make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 1, 1)
    assert get_result(m, TEAM_ID) == "E"


def test_get_result_loss():
    m = make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 0, 3)
    assert get_result(m, TEAM_ID) == "D"


def test_get_result_loss_away():
    m = make_match(1, WC_TOURNAMENT_ID, 999, TEAM_ID, 3, 1)
    assert get_result(m, TEAM_ID) == "D"


# ─── Transform: janela completa ───────────────────────────────────────────────

def test_transform_complete_window():
    matches = [
        make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 2, 0, timestamp=5000),
        make_match(2, WC_TOURNAMENT_ID, TEAM_ID, 999, 1, 1, timestamp=4800),
        make_match(3, WC_TOURNAMENT_ID, 999, TEAM_ID, 0, 2, timestamp=4600),
        make_match(4, FRIENDLY_ID,      TEAM_ID, 999, 3, 1, timestamp=4400),
        make_match(5, FRIENDLY_ID,      TEAM_ID, 999, 0, 2, timestamp=4200),
    ]
    window = make_window(matches)
    result = transform(TEAM_ID, window, {}, {})

    assert result["team_id"] == TEAM_ID
    assert result["data_quality"] == "complete"
    assert result["copa_count"] == 3
    assert result["friendly_count"] == 2
    # gols marcados: 2+1+2+3+0 = 8, avg = 1.6
    assert result["avg_goals_scored"] == 1.6
    # gols sofridos: 0+1+0+1+2 = 4, avg = 0.8
    assert result["avg_goals_conceded"] == 0.8
    assert "V" in result["form_sequence"]
    assert result["clean_sheets"] == 2  # partidas 1 e 3


# ─── Transform: janela parcial (divisor ≠ 5) ────────────────────────────────

def test_transform_partial_window_divisor():
    """Janela com 3 jogos: divisor deve ser 3, não 5."""
    matches = [
        make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 1, 0, timestamp=3000),
        make_match(2, FRIENDLY_ID,      TEAM_ID, 999, 0, 2, timestamp=2000),
        make_match(3, FRIENDLY_ID,      TEAM_ID, 999, 2, 0, timestamp=1000),
    ]
    window = make_window(matches)
    assert window.data_quality == "partial"
    result = transform(TEAM_ID, window, {}, {})
    # gols marcados: 1+0+2 = 3 / 3 = 1.0 (não 3/5 = 0.6)
    assert result["avg_goals_scored"] == 1.0
    assert result["data_quality"] == "partial"


# ─── Indicadores over/btts ────────────────────────────────────────────────────

def test_transform_over_indicators():
    matches = [
        make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 2, 1, timestamp=5000),  # 3 gols → over25; btts
        make_match(2, WC_TOURNAMENT_ID, TEAM_ID, 999, 1, 0, timestamp=4800),  # 1 gol  → não over15
        make_match(3, WC_TOURNAMENT_ID, TEAM_ID, 999, 2, 0, timestamp=4600),  # 2 gols → over15
        make_match(4, FRIENDLY_ID,      TEAM_ID, 999, 3, 2, timestamp=4400),  # 5 gols → over35; btts
        make_match(5, FRIENDLY_ID,      TEAM_ID, 999, 1, 1, timestamp=4200),  # 2 gols → over15; btts
    ]
    window = make_window(matches)
    result = transform(TEAM_ID, window, {}, {})

    assert result["over15_pct"] == 80.0   # 4/5
    assert result["over25_pct"] == 40.0   # 2/5
    assert result["over35_pct"] == 20.0   # 1/5
    assert result["btts_pct"] == 60.0     # 3/5 (partidas 1, 4, 5)


# ─── Tendência de gols ────────────────────────────────────────────────────────

def test_transform_trend():
    matches = [
        make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 3, 0, timestamp=5000),
        make_match(2, WC_TOURNAMENT_ID, TEAM_ID, 999, 3, 0, timestamp=4800),
        make_match(3, WC_TOURNAMENT_ID, TEAM_ID, 999, 3, 0, timestamp=4600),
        make_match(4, FRIENDLY_ID,      TEAM_ID, 999, 0, 0, timestamp=4400),
        make_match(5, FRIENDLY_ID,      TEAM_ID, 999, 0, 0, timestamp=4200),
    ]
    window = make_window(matches)
    result = transform(TEAM_ID, window, {}, {})
    # avg_3 = 3, avg_5 = 9/5 = 1.8, trend = 3 - 1.8 = 1.2
    assert result["trend_goals_3v5"] == 1.2


# ─── Forma (form_sequence) ────────────────────────────────────────────────────

def test_transform_form_sequence_away():
    """Time como visitante: perde 2-0, empata 1-1, vence 0-1."""
    matches = [
        make_match(1, WC_TOURNAMENT_ID, 999, TEAM_ID, 2, 0, timestamp=3000),  # D
        make_match(2, WC_TOURNAMENT_ID, 999, TEAM_ID, 1, 1, timestamp=2000),  # E
        make_match(3, WC_TOURNAMENT_ID, 999, TEAM_ID, 0, 1, timestamp=1000),  # V
    ]
    window = make_window(matches)
    result = transform(TEAM_ID, window, {}, {})
    assert result["form_sequence"] == "D E V"


# ─── Goals por tempo via incidents ───────────────────────────────────────────

def test_transform_goals_by_period():
    matches = [
        make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 2, 0, timestamp=2000),
        make_match(2, WC_TOURNAMENT_ID, TEAM_ID, 999, 1, 0, timestamp=1000),
    ]
    window = make_window(matches)

    incidents = {
        1: [
            {"incidentType": "goal", "period": 1, "team": {"id": TEAM_ID}},  # 1T
            {"incidentType": "goal", "period": 2, "team": {"id": TEAM_ID}},  # 2T
        ],
        2: [
            {"incidentType": "goal", "period": 2, "team": {"id": TEAM_ID}},  # 2T
        ],
    }

    result = transform(TEAM_ID, window, {}, incidents)
    # match 1: 1 gol no 1T, 1 gol no 2T | match 2: 0 no 1T, 1 no 2T
    # avg_1h = (1+0)/2 = 0.5 | avg_2h = (1+1)/2 = 1.0
    assert result["avg_goals_1h"] == 0.5
    assert result["avg_goals_2h"] == 1.0


# ─── Clean sheets ─────────────────────────────────────────────────────────────

def test_transform_clean_sheets():
    matches = [
        make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 1, 0, timestamp=5000),  # clean sheet
        make_match(2, WC_TOURNAMENT_ID, TEAM_ID, 999, 2, 1, timestamp=4800),  # not
        make_match(3, WC_TOURNAMENT_ID, 999, TEAM_ID, 0, 3, timestamp=4600),  # clean sheet (away)
        make_match(4, FRIENDLY_ID,      TEAM_ID, 999, 0, 0, timestamp=4400),  # clean sheet
        make_match(5, FRIENDLY_ID,      TEAM_ID, 999, 1, 2, timestamp=4200),  # not
    ]
    window = make_window(matches)
    result = transform(TEAM_ID, window, {}, {})
    assert result["clean_sheets"] == 3


# ─── Estatísticas via match_stats ─────────────────────────────────────────────

def test_transform_stats_from_sofascore():
    """Verifica extração de estatísticas do formato Sofascore."""
    matches = [
        make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 1, 0, timestamp=2000),
        make_match(2, WC_TOURNAMENT_ID, TEAM_ID, 999, 0, 0, timestamp=1000),
    ]
    window = make_window(matches)

    match_stats = {
        1: [
            {
                "groupName": "Shots",
                "statisticsItems": [
                    {"name": "Total shots", "home": "8", "away": "4"},
                    {"name": "Corner kicks", "home": "5", "away": "2"},
                ],
            },
            {
                "groupName": "Possession",
                "statisticsItems": [
                    {"name": "Ball possession", "home": "60%", "away": "40%"},
                ],
            },
        ],
        2: [
            {
                "groupName": "Shots",
                "statisticsItems": [
                    {"name": "Total shots", "home": "6", "away": "6"},
                    {"name": "Corner kicks", "home": "3", "away": "3"},
                ],
            },
            {
                "groupName": "Possession",
                "statisticsItems": [
                    {"name": "Ball possession", "home": "50%", "away": "50%"},
                ],
            },
        ],
    }

    result = transform(TEAM_ID, window, match_stats, {})
    # TEAM_ID é home em ambas as partidas
    assert result["avg_shots_total"] == 7.0    # (8+6)/2
    assert result["avg_corners"] == 4.0        # (5+3)/2
    assert result["avg_possession"] == 55.0    # (60+50)/2


# ─── over 3.5 escanteios ──────────────────────────────────────────────────────

def test_transform_over35_corners():
    matches = [
        make_match(1, WC_TOURNAMENT_ID, TEAM_ID, 999, 1, 0, timestamp=5000),
        make_match(2, WC_TOURNAMENT_ID, TEAM_ID, 999, 0, 0, timestamp=4800),
        make_match(3, WC_TOURNAMENT_ID, TEAM_ID, 999, 1, 0, timestamp=4600),
        make_match(4, FRIENDLY_ID,      TEAM_ID, 999, 2, 0, timestamp=4400),
        make_match(5, FRIENDLY_ID,      TEAM_ID, 999, 1, 0, timestamp=4200),
    ]
    window = make_window(matches)

    match_stats = {
        mid: [{"groupName": "Other", "statisticsItems": [
            {"name": "Corner kicks", "home": str(c), "away": "2"}
        ]}]
        for mid, c in [(1, 6), (2, 2), (3, 5), (4, 1), (5, 4)]
    }

    result = transform(TEAM_ID, window, match_stats, {})
    # Partidas com corners >= 4: mid 1 (6), mid 3 (5), mid 5 (4) = 3/5 = 60%
    assert result["over35_corners_pct"] == 60.0

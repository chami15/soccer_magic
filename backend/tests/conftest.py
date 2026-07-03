"""
Fixtures compartilhadas entre os testes do Soccer Magic backend.
"""
import sys
import os

# Garante que o backend/ está no path para todos os testes
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

WC_TOURNAMENT_ID = 16  # ID real da Copa do Mundo no Sofascore


def make_match(
    match_id: int = 1,
    home_id: int = 10,
    away_id: int = 20,
    home_goals: int = 2,
    away_goals: int = 1,
    ht_home: int = 1,
    ht_away: int = 0,
    status: str = "finished",
    tournament_id: int = WC_TOURNAMENT_ID,
    timestamp: int = 1750000000,
    custom_id: str | None = "abc123",
    group_name: str | None = "Group A",
    round_num: int | None = 1,
    city: str | None = "Rio de Janeiro",
) -> dict:
    """Cria um evento de partida no formato Sofascore."""
    return {
        "id": match_id,
        "customId": custom_id,
        "startTimestamp": timestamp,
        "homeTeam": {"id": home_id, "name": "Home FC"},
        "awayTeam": {"id": away_id, "name": "Away FC"},
        "homeScore": {"current": home_goals, "period1": ht_home},
        "awayScore": {"current": away_goals, "period1": ht_away},
        "status": {"type": status},
        "tournament": {
            "uniqueTournament": {"id": tournament_id},
            "groupName": group_name,
            "groupSign": None,
        },
        "roundInfo": {"round": round_num},
        "venue": {"city": {"name": city}},
    }


def make_stats_groups(
    posse_home: int = 60,
    chutes_home: int = 10,
    escanteios_home: int = 5,
    passes_home: int = 400,
    passes_certos_home: int = 360,
    cartao_amarelo_home: int = 1,
    posse_away: int = 40,
    chutes_away: int = 5,
    escanteios_away: int = 3,
    passes_away: int = 280,
    passes_certos_away: int = 230,
    cartao_amarelo_away: int = 2,
) -> list[dict]:
    """Cria payload de estatísticas no formato Sofascore."""
    return [
        {
            "groupName": "Match overview",
            "statisticsItems": [
                {
                    "key": "ballPossession",
                    "homeValue": posse_home,
                    "awayValue": posse_away,
                },
                {
                    "key": "totalShotsOnGoal",
                    "homeValue": chutes_home,
                    "awayValue": chutes_away,
                },
                {
                    "key": "cornerKicks",
                    "homeValue": escanteios_home,
                    "awayValue": escanteios_away,
                },
                {
                    "key": "yellowCards",
                    "homeValue": cartao_amarelo_home,
                    "awayValue": cartao_amarelo_away,
                },
            ],
        },
        {
            "groupName": "Passes",
            "statisticsItems": [
                {
                    "key": "passes",
                    "homeValue": passes_home,
                    "awayValue": passes_away,
                },
                {
                    "key": "accuratePasses",
                    "homeValue": passes_certos_home,
                    "awayValue": passes_certos_away,
                },
            ],
        },
    ]

"""
Soccer Magic — Schemas do agente (output_schema)
Campos numéricos só podem ser preenchidos com valores vindos das tools.
qualitative_notes é o único campo livre (texto, vindo do Tavily).
"""
from pydantic import BaseModel


class MatchCollected(BaseModel):
    match_id: int
    opponent_name: str
    statistics: list[dict]
    incidents: list[dict]


class TeamDailyReport(BaseModel):
    team_id: int
    team_name: str
    matches_collected: list[MatchCollected] = []
    qualitative_notes: str | None = None
    collection_errors: list[str] = []

"""
Soccer Magic — Agente de coleta diária
O agente orquestra as tools (decide o que chamar e com quais IDs) e monta o
output_schema copiando os valores retornados pelas tools. Ele nunca extrai
ou estima número por conta própria — campos numéricos só existem dentro de
MatchCollected.statistics/incidents, que são o retorno bruto das tools.
"""
import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat

from agents.schemas import TeamDailyReport
from agents.tools import (
    enrich_context,
    get_h2h_events,
    get_match_incidents,
    get_match_statistics,
    get_team_goal_distributions,
    get_team_recent_matches,
)

INSTRUCTIONS = [
    "Você coleta dados de uma seleção de futebol para inserção em banco de dados.",
    "Use get_team_recent_matches para descobrir as partidas recentes do time.",
    "Para cada partida relevante, use get_match_statistics e get_match_incidents.",
    "Use get_team_goal_distributions para a distribuição de gols por intervalo na temporada.",
    "Use get_h2h_events (com o customId da partida, não o id numérico) para o histórico de confrontos diretos.",
    "Os campos statistics, incidents, goal_distributions e h2h_events devem ser exatamente o retorno dessas tools — nunca resuma, estime ou invente valores.",
    "Use enrich_context apenas para qualitative_notes (texto livre sobre lesões/notícias). Nunca use seu retorno para preencher campos numéricos.",
    "Se uma tool falhar, registre a falha em collection_errors e siga para a próxima partida.",
]


def build_agent(sofascore_client: httpx.Client) -> Agent:
    return Agent(
        model=OpenAIChat(id="gpt-4o-mini"),
        tools=[
            get_team_recent_matches,
            get_match_statistics,
            get_match_incidents,
            get_team_goal_distributions,
            get_h2h_events,
            enrich_context,
        ],
        output_schema=TeamDailyReport,
        dependencies={"sofascore_client": sofascore_client},
        instructions=INSTRUCTIONS,
    )


def collect_team_report(sofascore_client: httpx.Client, team_id: int, team_name: str) -> TeamDailyReport:
    agent = build_agent(sofascore_client)
    response = agent.run(
        f"Colete os dados da seleção {team_name} (team_id={team_id}) para hoje."
    )
    return response.content

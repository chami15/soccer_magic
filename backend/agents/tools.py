"""
Soccer Magic — Tools do agente
Tools numéricas (Sofascore) são wrappers diretos do collector.py: a LLM nunca
extrai número de texto, só decide quais chamar e com quais IDs.
enrich_context é a única tool que usa Tavily, e seu retorno é sempre texto
qualitativo — nunca usado para popular campos numéricos do banco.
"""
from agno.agent import Agent
from agno.tools.tavily import TavilyTools

from pipeline import collector

_tavily = TavilyTools()


def get_team_recent_matches(agent: Agent, team_id: int, count: int = 10) -> list[dict]:
    """Retorna as últimas partidas encerradas de um time (determinístico, via Sofascore)."""
    client = agent.dependencies["sofascore_client"]
    return collector.get_team_recent_matches(client, team_id, count=count)


def get_match_statistics(agent: Agent, match_id: int) -> list[dict]:
    """Retorna as estatísticas brutas de uma partida (determinístico, via Sofascore)."""
    client = agent.dependencies["sofascore_client"]
    return collector.get_match_statistics(client, match_id)


def get_match_incidents(agent: Agent, match_id: int) -> list[dict]:
    """Retorna os incidentes (gols, cartões, etc.) de uma partida (determinístico, via Sofascore)."""
    client = agent.dependencies["sofascore_client"]
    return collector.get_match_incidents(client, match_id)


def get_team_goal_distributions(agent: Agent, team_id: int) -> list[dict]:
    """Retorna a distribuição de gols por intervalo de 15min da temporada (determinístico, via Sofascore)."""
    client = agent.dependencies["sofascore_client"]
    return collector.get_team_goal_distributions(client, team_id)


def get_h2h_events(agent: Agent, custom_id: str) -> list[dict]:
    """Retorna o histórico de confrontos diretos de uma partida (determinístico, via Sofascore).
    custom_id é o identificador curto do evento (ex: 'VTbsYUb'), não o match_id numérico."""
    client = agent.dependencies["sofascore_client"]
    return collector.get_h2h_events(client, custom_id)


def enrich_context(team_name: str, date: str) -> str:
    """Busca contexto qualitativo (lesões, notícias) via Tavily. Nunca retorna números a inserir no banco."""
    result = _tavily.web_search_using_tavily(f"{team_name} seleção notícias lesões {date}", max_results=3)
    return result

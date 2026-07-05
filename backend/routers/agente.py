from fastapi import APIRouter, HTTPException

from resolvers import agente as resolver

router = APIRouter(prefix="/api/agente", tags=["Agente"])


@router.get("/analise/{partida_id}")
async def analise_partida(partida_id: int):
    """
    Invoca o agente de análise para a partida informada.
    Retorna JSON com previsão de placar, mercados favoritos,
    análise narrativa e 3 bilhetes (baixo/médio/alto risco).
    """
    return await resolver.resolver_analise_partida(partida_id)

from fastapi import APIRouter, HTTPException

from resolvers import agente as resolver

router = APIRouter(prefix="/api/agente", tags=["Agente"])


@router.get("/analise/{partida_id}")
def analise_partida(partida_id: int):
    """
    Invoca o agente de análise para a partida informada.
    Retorna JSON com previsão de placar, mercados favoritos,
    análise narrativa e 3 bilhetes (baixo/médio/alto risco).
    """
    try:
        return resolver.resolver_analise_partida(partida_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

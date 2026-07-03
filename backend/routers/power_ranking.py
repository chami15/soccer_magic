from fastapi import APIRouter, HTTPException

from resolvers import power_ranking as resolver

router = APIRouter(prefix="/api/power-ranking", tags=["Power Ranking"])


@router.get("/{selecao_id}")
def power_ranking_selecao(selecao_id: int):
    try:
        return resolver.buscar_power_ranking(selecao_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

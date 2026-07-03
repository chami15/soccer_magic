from fastapi import APIRouter, HTTPException

from resolvers import h2h as resolver

router = APIRouter(prefix="/api/h2h", tags=["H2H"])


@router.get("/{selecao_a_id}/{selecao_b_id}")
def confrontos_diretos(selecao_a_id: int, selecao_b_id: int):
    try:
        return resolver.buscar_h2h(selecao_a_id, selecao_b_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

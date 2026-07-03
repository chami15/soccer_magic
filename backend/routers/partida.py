from fastapi import APIRouter, HTTPException

from resolvers import partida as resolver

router = APIRouter(prefix="/api/partidas", tags=["Partidas"])


@router.get("/{partida_id}")
def detalhe_partida(partida_id: int):
    try:
        return resolver.buscar_partida(partida_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/selecao/{selecao_id}")
def partidas_da_selecao(selecao_id: int):
    try:
        return resolver.listar_partidas_selecao(selecao_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

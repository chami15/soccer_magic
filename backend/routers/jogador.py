from fastapi import APIRouter, HTTPException

from resolvers import jogador as resolver

router = APIRouter(prefix="/api/jogadores", tags=["Jogadores"])


@router.get("/selecao/{selecao_id}")
def jogadores_da_selecao(selecao_id: int):
    try:
        return resolver.listar_jogadores_selecao(selecao_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

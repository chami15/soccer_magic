from fastapi import APIRouter, HTTPException

from resolvers import selecao_estatistica as resolver

router = APIRouter(prefix="/api/selecoes", tags=["Seleções"])


# ─────────────────────────────────────────────
# Estatísticas
# ─────────────────────────────────────────────

@router.get("/{selecao_id}/estatisticas")
def estatisticas_selecao(selecao_id: int):
    try:
        return resolver.resolver_estatisticas_selecao(selecao_id)
    except Exception as e:
        raise HTTPException(500, str(e))

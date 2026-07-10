from fastapi import APIRouter, HTTPException

from resolvers import selecao_estatistica as resolver
from utils.query_executor import executar_query

router = APIRouter(prefix="/api/selecoes", tags=["Seleções"])


# ─────────────────────────────────────────────
# Catálogo (lista todas as seleções)
# ─────────────────────────────────────────────

@router.get("")
def listar_selecoes():
    try:
        rows = executar_query("selecao:select_all", params=())
        return {"total": len(rows), "selecoes": rows}
    except Exception as e:
        raise HTTPException(500, str(e))


# ─────────────────────────────────────────────
# Estatísticas
# ─────────────────────────────────────────────

@router.get("/{selecao_id}/estatisticas")
def estatisticas_selecao(selecao_id: int):
    try:
        return resolver.resolver_estatisticas_selecao(selecao_id)
    except Exception as e:
        raise HTTPException(500, str(e))

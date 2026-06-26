"""
Router — endpoints de seleção para o frontend.
"""

from fastapi import APIRouter

from resolvers.selecao_estatistica import resolver_estatisticas_selecao

router = APIRouter(prefix="/selecoes", tags=["selecoes"])


@router.get("/{selecao_id}/estatisticas")
def get_estatisticas_selecao(selecao_id: int) -> dict:
    return resolver_estatisticas_selecao(selecao_id)

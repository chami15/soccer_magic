from fastapi import APIRouter, HTTPException, Query

from resolvers import calendario as resolver

router = APIRouter(prefix="/api/calendario", tags=["Calendário"])


@router.get("/proximas")
def proximas_partidas(limit: int = Query(default=20, ge=1, le=100)):
    try:
        return resolver.listar_proximas_partidas(limit)
    except Exception as e:
        raise HTTPException(500, str(e))

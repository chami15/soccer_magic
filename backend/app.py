"""
Soccer Magic — API FastAPI

Rodar localmente:
    cd backend
    uvicorn app:app --reload
"""

from fastapi import FastAPI

from routers.selecao import router as selecao_router
from routers.partida import router as partida_router
from routers.jogador import router as jogador_router
from routers.h2h import router as h2h_router
from routers.power_ranking import router as power_ranking_router
from routers.calendario import router as calendario_router
from routers.agente import router as agente_router

app = FastAPI(title="Soccer Magic API")

app.include_router(selecao_router)
app.include_router(partida_router)
app.include_router(jogador_router)
app.include_router(h2h_router)
app.include_router(power_ranking_router)
app.include_router(calendario_router)
app.include_router(agente_router)

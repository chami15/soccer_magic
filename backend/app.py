"""
Soccer Magic — API FastAPI

Rodar localmente:
    cd backend
    uvicorn app:app --reload
"""

from fastapi import FastAPI

from routers.selecao import router as selecao_router

app = FastAPI(title="Soccer Magic API")

app.include_router(selecao_router)

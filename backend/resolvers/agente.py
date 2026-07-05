"""
Resolver — invoca o agente de análise e trata erros de execução.

Cache em memória com TTL de 1 hora por partida_id. Evita re-executar o LLM
a cada chamada repetida para a mesma partida durante a janela de TTL.
"""

import time
import traceback

from fastapi import HTTPException

from agente.agente import analisar_partida

CACHE_TTL_SEGUNDOS = 3600  # 1 hora

# {partida_id: {"resultado": dict, "timestamp": float}}
_cache: dict[int, dict] = {}


def _cache_get(partida_id: int) -> dict | None:
    entrada = _cache.get(partida_id)
    if entrada is None:
        return None
    if time.monotonic() - entrada["timestamp"] > CACHE_TTL_SEGUNDOS:
        del _cache[partida_id]
        return None
    return entrada["resultado"]


def _cache_set(partida_id: int, resultado: dict) -> None:
    _cache[partida_id] = {"resultado": resultado, "timestamp": time.monotonic()}


async def resolver_analise_partida(partida_id: int) -> dict:
    cached = _cache_get(partida_id)
    if cached is not None:
        print(f"[cache] partida_id={partida_id} servido do cache (TTL {CACHE_TTL_SEGUNDOS}s)")
        return cached

    try:
        resultado = await analisar_partida(partida_id)
        _cache_set(partida_id, resultado)
        return resultado
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro inesperado no agente: {type(exc).__name__}: {exc}\n{tb}",
        )

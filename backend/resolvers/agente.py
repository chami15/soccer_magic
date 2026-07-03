"""
Resolver — invoca o agente de análise e trata erros de execução.
"""

import traceback

from fastapi import HTTPException

from agente.agente import analisar_partida


def resolver_analise_partida(partida_id: int) -> dict:
    try:
        return analisar_partida(partida_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro inesperado no agente: {type(exc).__name__}: {exc}\n{tb}",
        )

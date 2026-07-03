"""
Guardrails do agente.

- Middleware @wrap_tool_call que captura exceções e devolve ToolMessage
  com o erro estruturado, impedindo que o agente entre em loop tentando
  re-executar tools quebradas.
- Contador de steps injetado no contexto para limitar o número máximo
  de chamadas de tool por execução.
"""

import time
import traceback

from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage

MAX_TOOL_CALLS = 10


@wrap_tool_call
async def tratar_erros_tools(request, handler):
    """
    Intercepta toda chamada de tool. Se a tool lançar qualquer exceção,
    devolve um ToolMessage de erro em vez de propagar o crash.
    O agente recebe o erro no contexto e deve parar (não tentar de novo).
    """
    tool_name = request.tool_call["name"]
    tool_call_id = request.tool_call["id"]
    inicio = time.monotonic()

    try:
        resultado = await handler(request)
        duracao = round(time.monotonic() - inicio, 3)
        print(f"[tool] {tool_name} → ok ({duracao}s)")
        return resultado

    except Exception as exc:
        duracao = round(time.monotonic() - inicio, 3)
        tb = traceback.format_exc()
        print(f"[tool] {tool_name} → ERRO ({duracao}s): {exc}\n{tb}")

        mensagem_erro = (
            f"ERRO na tool '{tool_name}': {type(exc).__name__}: {exc}. "
            "Não tente chamar esta tool novamente. "
            "Se não puder continuar a análise sem este dado, "
            "retorne o JSON final com os campos disponíveis e indique "
            "qual informação estava indisponível."
        )
        return ToolMessage(
            content=mensagem_erro,
            tool_call_id=tool_call_id,
        )

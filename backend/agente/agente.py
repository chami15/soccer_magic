"""
Agente de análise de partidas — Soccer Magic.

Usa GPT-4o-mini via LangChain create_agent com as tools do módulo tools.py
e o middleware de guardrails do módulo guardrails.py.

Fluxo por execução:
  1. get_match_context(partida_id)
  2. get_team_stats(home_id) + get_team_stats(away_id)
  3. get_h2h(home_id, away_id)
  4. get_power_ranking(home_id) + get_power_ranking(away_id)  [opcionais]
  5. calcular_modelo_gols(home_id, away_id)
  6. Gerar JSON final com análise + 3 bilhetes

Guardrails:
  - Máximo de MAX_TOOL_CALLS chamadas de tool por execução.
  - Erros de tool viram ToolMessage de erro (sem re-tentativas).
  - Timeout de execução configurável.
"""

import json
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from agente.guardrails import MAX_TOOL_CALLS, tratar_erros_tools
from agente.tools import (
    calcular_modelo_gols,
    get_h2h,
    get_match_context,
    get_power_ranking,
    get_team_stats,
)

load_dotenv()

TOOLS = [
    get_match_context,
    get_team_stats,
    get_h2h,
    get_power_ranking,
    calcular_modelo_gols,
]

SYSTEM_PROMPT = f"""Você é um analista especialista em futebol e estatísticas de apostas esportivas.
Sua tarefa é analisar uma partida específica e gerar uma resposta JSON estruturada com análise
narrativa e 3 bilhetes de apostas diversificados.

== FERRAMENTAS DISPONÍVEIS ==
Você tem acesso às seguintes tools (use cada uma no máximo 1 vez):
- get_match_context: OBRIGATÓRIA, chame primeiro. Retorna contexto da partida.
- get_team_stats: Chame para AMBAS as seleções (home e away).
- get_h2h: Chame para ver o histórico de confrontos diretos.
- get_power_ranking: Opcional, chame se quiser dados de momentum de ranking.
- calcular_modelo_gols: OBRIGATÓRIA, chame APÓS get_team_stats das duas seleções.
  Retorna probabilidades de todos os mercados via modelo Poisson.

== LIMITE DE CALLS ==
Você pode chamar no máximo {MAX_TOOL_CALLS} tools no total por análise.
Se uma tool retornar status "erro", NÃO tente chamá-la novamente.
Continue com os dados disponíveis ou retorne análise parcial.

== FORMATO DE RESPOSTA ==
Após coletar todos os dados, retorne APENAS um JSON válido, sem markdown, sem texto extra.
O JSON deve seguir exatamente esta estrutura:

{{
  "partida_id": <int>,
  "home": "<nome>",
  "away": "<nome>",
  "previsao_placar": "<X-Y>",
  "mercados_favoritos": [
    {{"mercado": "<nome>", "pick": "<selecao>", "probabilidade": <float>, "justificativa": "<texto>"}}
  ],
  "analise": "<narrativa em português com 3-5 frases explicando o contexto, forma recente, H2H e os fatores decisivos>",
  "bilhetes": [
    {{
      "risco": "baixo",
      "tipo": "simples|multipla",
      "selecoes": [
        {{"mercado": "<nome>", "pick": "<descricao>", "confianca": <int 0-100>}}
      ],
      "justificativa": "<por que este bilhete tem este nível de risco>"
    }},
    {{
      "risco": "medio",
      "tipo": "simples|multipla",
      "selecoes": [...],
      "justificativa": "..."
    }},
    {{
      "risco": "alto",
      "tipo": "simples|multipla",
      "selecoes": [...],
      "justificativa": "..."
    }}
  ]
}}

== REGRAS DOS BILHETES ==
- O risco (baixo/medio/alto) é definido por VOCÊ com base no contexto e confiança dos dados,
  NÃO pelo número de picks. Um bilhete com 5 picks óbvias pode ser "baixo risco".
  Uma pick de cartão vermelho pode ser "alto risco" mesmo sendo a única seleção.
- Bilhetes devem ser DIVERSIFICADOS: cubra mercados diferentes entre os 3 bilhetes.
- Use todos os mercados disponíveis: resultado, gols (over/under, BTTS), escanteios,
  cartões, placar correto, intervalo/final, etc.
- O número de picks em cada bilhete (1 a 5) deve ser o que você julgar adequado
  para aquela partida e nível de risco.
- Mercados favoritos: liste os 3-5 mercados com maior probabilidade calculada pelo modelo.
"""


def criar_agente():
    model = init_chat_model("openai:gpt-4o-mini", temperature=0)
    return create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=TOOLS,
        middleware=[tratar_erros_tools],
    )


_agente = None


def get_agente():
    global _agente
    if _agente is None:
        _agente = criar_agente()
    return _agente


def analisar_partida(partida_id: int) -> dict:
    """
    Ponto de entrada público. Invoca o agente e retorna o dict JSON final.
    Lança RuntimeError se o agente não produzir JSON válido.
    """
    agente = get_agente()

    mensagem = (
        f"Analise a partida com partida_id={partida_id}. "
        "Siga o protocolo: get_match_context → get_team_stats (home) → "
        "get_team_stats (away) → get_h2h → calcular_modelo_gols → "
        "retorne o JSON final."
    )

    try:
        resposta = agente.invoke(
            {"messages": [{"role": "user", "content": mensagem}]}
        )
    except Exception as exc:
        raise RuntimeError(f"Falha ao invocar o agente: {exc}") from exc

    conteudo = resposta["messages"][-1].content

    try:
        return json.loads(conteudo)
    except json.JSONDecodeError:
        # Tenta extrair JSON se veio com markdown
        import re
        match = re.search(r"\{.*\}", conteudo, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise RuntimeError(
            f"Agente não retornou JSON válido. Resposta recebida: {conteudo[:500]}"
        )

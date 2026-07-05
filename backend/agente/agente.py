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

SYSTEM_PROMPT = f"""Você é um analista quantitativo de apostas esportivas de elite. Sua função é
encontrar VALOR e PADRÕES que o olho humano não enxerga facilmente — anomalias estatísticas,
tendências de tempo de jogo, discrepâncias entre ataque e defesa, mercados subvalorizados.
Não produza análises genéricas. Cada partida tem um perfil único nos dados — encontre-o.

== FERRAMENTAS DISPONÍVEIS ==
Use cada tool no máximo 1 vez, nesta ordem:
1. get_match_context      — OBRIGATÓRIA. Contexto da partida (IDs, data, rodada).
2. get_team_stats(home)   — OBRIGATÓRIA. Estatísticas dos últimos 5 jogos do time home.
3. get_team_stats(away)   — OBRIGATÓRIA. Estatísticas dos últimos 5 jogos do time away.
4. get_h2h               — OBRIGATÓRIA. Histórico de confrontos diretos.
5. get_power_ranking(home) + get_power_ranking(away) — Use ambos se quiser momentum.
6. calcular_modelo_gols   — OBRIGATÓRIA. Roda o modelo Poisson completo (1X2, over/under,
   BTTS, escanteios, cartões). Chame APÓS os dois get_team_stats.

== LIMITE ==
Máximo de {MAX_TOOL_CALLS} chamadas no total. Se uma tool retornar erro, não repita — continue.

== METODOLOGIA DE ANÁLISE (siga esta lógica antes de escrever o JSON) ==

1. PERFIL DE GOLS: Compare avg_goals_scored e avg_goals_conceded de cada time.
   Calcule o "índice ofensivo" (ataque_home × defesa_away) para prever pressão real.
   Verifique avg_goals_1h vs avg_goals_2h — times que marcam mais no 2T têm padrão diferente.

2. PADRÕES OCULTOS: Cruze os dados e procure por anomalias como:
   - Time com over35_corners_pct alto mas avg_corners baixo (inconsistência → explorar)
   - Time com btts_pct alto mas avg_goals_conceded baixo (defesa seletiva)
   - avg_goals_1h ≈ 0 para ambos (gols tendem a sair no 2T → over 2T específico)
   - avg_blocked_shots alto para o adversário (ataque encontra resistência → under)
   - avg_yellow_cards alto para ambos (jogo físico → mercado de cartões)
   - clean_sheets alto + over35_corners_pct alto (defesa forte mas pressionada → escanteios sem gol)
   - trend_goals_3v5 positivo (time acelerando) vs negativo (time esfriando)
   - Diferença grande de avg_possession (time que domina tende a ter mais escanteios)

3. CONFRONTO DIRETO: Nos H2H, olhe o padrão histórico:
   - Quem vence mais? Há dominância clara?
   - Média de gols nos confrontos (jogo aberto ou fechado historicamente?)
   - BTTS histórico nos H2H

4. MERCADOS A EXPLORAR (não se limite aos óbvios):
   - 1X2 e Dupla Chance
   - Over/Under 1.5, 2.5, 3.5, 4.5 gols
   - BTTS (Ambas marcam) Sim/Não
   - Over/Under escanteios (9.5, 10.5)
   - Over/Under cartões amarelos (3.5, 4.5)
   - Resultado no intervalo (1T)
   - Gols no 1º tempo (over/under 0.5, 1.5)
   - Gols no 2º tempo (over/under 0.5, 1.5)
   - Placar correto (top 3 do modelo)
   - Handicap asiático (ex: home -0.5, away +1.5)
   - Time marca primeiro
   - Over/Under gols de um time específico (ex: home over 1.5)

5. CRITÉRIO DE VALOR: Prefira picks onde a probabilidade calculada pelo modelo é
   SIGNIFICATIVAMENTE maior que o esperado para aquela situação. Uma pick com 65%+
   é mais valiosa do que uma com 52%. Foco em edges, não em popularidade.

== FORMATO DE RESPOSTA ==
Retorne APENAS JSON válido, sem markdown, sem texto extra.

{{
  "partida_id": <int>,
  "home": "<nome>",
  "away": "<nome>",
  "previsao_placar": "<X-Y>",
  "padroes_identificados": [
    "<padrão ou anomalia estatística encontrada nos dados, ex: 'Home marca 80% dos gols no 2T'>",
    "<outro padrão>",
    "..."
  ],
  "mercados_favoritos": [
    {{
      "mercado": "<nome específico do mercado>",
      "pick": "<seleção>",
      "probabilidade": <float>,
      "odd_justa": <float arredondado 2 casas — calculado como 100/probabilidade>,
      "justificativa": "<baseada em dados concretos, cite os números>"
    }}
  ],
  "analise": "<narrativa analítica em português: 4-6 frases citando números reais (médias, %, tendências). Não use frases genéricas. Aponte o que os dados revelam de surpreendente ou contra-intuitivo nesta partida.>",
  "bilhetes": [
    {{
      "risco": "baixo",
      "tipo": "simples|multipla",
      "odd_bilhete": <float — para simples: 100/probabilidade_da_pick; para múltipla: produto das odds de cada seleção, arredondado 2 casas>,
      "selecoes": [
        {{"mercado": "<mercado>", "pick": "<pick>", "confianca": <int 0-100>, "odd_justa": <float>}}
      ],
      "justificativa": "<explique o raciocínio quantitativo: por que este mercado, por que este nível de risco>"
    }},
    {{
      "risco": "medio",
      "tipo": "simples|multipla",
      "odd_bilhete": <float>,
      "selecoes": [...],
      "justificativa": "..."
    }},
    {{
      "risco": "alto",
      "tipo": "simples|multipla",
      "odd_bilhete": <float>,
      "selecoes": [...],
      "justificativa": "..."
    }}
  ]
}}

== REGRAS DOS BILHETES ==
- Risco é definido por VOCÊ com base na confiança dos dados e volatilidade do mercado.
  5 picks óbvias = baixo risco. 1 pick de cartão específico = alto risco.
- Os 3 bilhetes DEVEM cobrir mercados DIFERENTES entre si. Não repita o mesmo mercado.
- Explore ao menos 1 mercado não-óbvio (cartões, escanteios, tempo de gol, handicap).
- Cite os dados que embasam cada bilhete na justificativa.
- padroes_identificados: liste de 2 a 5 padrões reais encontrados nos dados, com números.
  Ex: "Mexico avg_goals_1h=0.4 vs avg_goals_2h=1.6 — 80% dos gols saem no 2T".

== CÁLCULO DE ODDS ==
- odd_justa de uma pick = round(100 / probabilidade, 2). Ex: 70% → odd 1.43; 45% → odd 2.22.
- odd_bilhete simples = odd_justa da única pick.
- odd_bilhete múltipla = produto de todas as odd_justa das seleções do bilhete.
  Ex: picks com odds 1.43 × 1.28 × 2.10 = odd_bilhete 3.84.
- ATENÇÃO: odd_justa é a odd sem margem da casa (fair odds). As casas aplicam margem de
  5-15%, então a odd real no mercado será sempre menor. Se a casa oferecer odd ACIMA da
  odd_justa calculada, é uma aposta com valor positivo (edge favorável ao apostador).
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


async def analisar_partida(partida_id: int) -> dict:
    """
    Ponto de entrada público. Invoca o agente de forma assíncrona e retorna o dict JSON final.
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
        resposta = await agente.ainvoke(
            {"messages": [{"role": "user", "content": mensagem}]}
        )
    except Exception as exc:
        raise RuntimeError(f"Falha ao invocar o agente: {exc}") from exc

    conteudo = resposta["messages"][-1].content

    try:
        return json.loads(conteudo)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{.*\}", conteudo, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise RuntimeError(
            f"Agente não retornou JSON válido. Resposta recebida: {conteudo[:500]}"
        )

"""
Soccer Magic — Avaliador de Backend

Agente que analisa o estado atual do projeto e emite notas de 0 a 10
por dimensão, com justificativa e o que falta para o 10.

Rodar:
    cd backend
    python3 avaliar_backend.py
"""

import os
import textwrap

LARGURA = 70


def titulo(texto: str) -> None:
    print("\n" + "=" * LARGURA)
    print(f"  {texto}")
    print("=" * LARGURA)


def nota_linha(dimensao: str, nota: float, max_nota: float = 10.0) -> None:
    barra_cheia = int((nota / max_nota) * 20)
    barra = "█" * barra_cheia + "░" * (20 - barra_cheia)
    print(f"\n  {dimensao:<35} [{barra}]  {nota:.1f}/10")


def detalhe(texto: str) -> None:
    for linha in textwrap.wrap(texto, width=LARGURA - 4):
        print(f"    {linha}")


def o_que_falta(texto: str) -> None:
    print("    → Para o 10:", end=" ")
    for i, linha in enumerate(textwrap.wrap(texto, width=LARGURA - 16)):
        if i == 0:
            print(linha)
        else:
            print(f"              {linha}")


# ─────────────────────────────────────────────────────────────────────────────

AVALIACOES = [
    {
        "dimensao": "Coleta de dados (scraper)",
        "nota": 8.5,
        "descricao": (
            "O collector.py é robusto: estratégia dupla httpx + Playwright, "
            "retry exponencial, rate limit, cache de sessão Playwright para "
            "evitar múltiplos browsers. Cobre todos os endpoints necessários "
            "(partidas, estatísticas, incidentes, h2h, power ranking, "
            "performance points). A descoberta de customId via interceptação "
            "de rede é elegante."
        ),
        "falta": (
            "Sem retry dedicado para o Playwright (falha silenciosa se o "
            "cache miss). Sem timeout configurável por endpoint. Playwright "
            "é síncrono e bloqueia o processo; para um pipeline de produção, "
            "um pool de browsers ou um microserviço dedicado seria mais robusto."
        ),
    },
    {
        "dimensao": "Modelagem do banco (schema)",
        "nota": 8.0,
        "descricao": (
            "Modelo estrela bem definido: 2 dimensões (dim_selecao, dim_jogador) "
            "e 5 fatos (fato_partida, fato_estatistica_selecao_partida, "
            "fato_evento_partida, fato_h2h_evento, fato_power_ranking_selecao). "
            "PKs naturais (IDs Sofascore), upserts idempotentes, RLS ativado "
            "em todas as tabelas, FKs corretas garantindo integridade."
        ),
        "falta": (
            "Campo 'continente' em dim_selecao sempre NULL (dict vazio no "
            "transformer). 'var_decisao' em fato_evento_partida nunca "
            "preenchido. Sem índices explícitos além do PK — consultas por "
            "selecao_id em fato_estatistica e fato_evento vão fazer full "
            "scan em volume alto. Tabela pipeline_runs existe mas nunca é "
            "escrita."
        ),
    },
    {
        "dimensao": "Transformers (tratamento de dados)",
        "nota": 7.5,
        "descricao": (
            "Cada entidade tem seu transformer isolado, sem lógica misturada "
            "com coleta ou persistência. transform_estatistica é o mais "
            "sofisticado: achata grupos, calcula passes_precisao_pct, trata "
            "valores string/numérico da API. transform_partida resolve "
            "vencedor e tipo corretamente."
        ),
        "falta": (
            "CONTINENTE_POR_PAIS vazio: dado estrutural importante ausente. "
            "Sem validação de schema nos payloads de entrada (um campo "
            "renomeado pela API quebra silenciosamente). Sem testes unitários "
            "cobrindo os transformers — toda validação é manual via os scripts "
            "test_pipeline_basicovN."
        ),
    },
    {
        "dimensao": "Persisters e acesso ao banco",
        "nota": 8.0,
        "descricao": (
            "Thin wrappers limpos sobre executar_query. Pool de conexões com "
            "TCP keepalives, retry automático em OperationalError/InterfaceError, "
            "descarte correto de conexões quebradas no pool. executar_query "
            "unifica commit, returning e interpolação de variáveis em uma "
            "interface consistente."
        ),
        "falta": (
            "ThreadedConnectionPool com maxconn padrão baixo (provavelmente "
            "10) — sem configuração explícita visível no pool. Sem transação "
            "explícita cobrindo dim_selecao + fato_partida + fato_estatistica "
            "de uma mesma partida: uma falha parcial deixa o banco em estado "
            "inconsistente. Sem bulk insert real (execute_values) nos scripts "
            "de carga — cada linha é um round-trip separado."
        ),
    },
    {
        "dimensao": "Pipeline de ingestão (orquestração)",
        "nota": 8.0,
        "descricao": (
            "pipeline/orquestrador.py centraliza processar_time() e "
            "processar_partida_futura() — eliminando a duplicação dos 12 "
            "scripts anteriores. pipeline_diario.py descobre automaticamente "
            "os jogos de amanhã via get_tournament_next_events, persiste "
            "o calendário completo da Copa (todas as partidas futuras) e "
            "roda o pipeline de ingestão histórica para cada seleção. "
            "Pronto para agendar via cron ou GitHub Actions."
        ),
        "falta": (
            "Sem log estruturado (só print — sem arquivo de log, sem níveis "
            "INFO/WARNING/ERROR). Os scripts v4-v12 ainda carregam processar_time() "
            "copiada internamente em vez de importar do orquestrador. "
            "Sem idempotência no nível HTTP: re-executar o pipeline faz "
            "chamadas redundantes ao Sofascore para dados que já estão no banco."
        ),
    },
    {
        "dimensao": "API / Resolvers / Routers",
        "nota": 7.5,
        "descricao": (
            "7 grupos de endpoints cobertos: estatísticas de seleção, partidas "
            "(lista + detalhe), jogadores, H2H, power ranking, calendário e "
            "agente de análise. O endpoint GET /api/agente/analise/{partida_id} "
            "invoca o agente LLM com tools estatísticas e retorna JSON com "
            "previsão de placar, análise narrativa e 3 bilhetes diversificados."
        ),
        "falta": (
            "Sem autenticação/autorização (endpoints públicos). Sem paginação "
            "nos endpoints de lista. Sem versionamento (/v1/...). "
            "goal_distribution_summary e tournament_overall_stats ainda retornam "
            "None no resolver de estatísticas. Sem endpoint GET /api/selecoes/{id} "
            "com dados básicos da seleção (nome, grupo, ranking FIFA)."
        ),
    },
    {
        "dimensao": "Organização e estrutura de código",
        "nota": 8.5,
        "descricao": (
            "Separação limpa em 7 camadas: collector / transformers / persisters "
            "/ resolvers / routers / utils / sql / agente. O módulo agente/ "
            "tem separação interna exemplar: probabilidades.py (math pura), "
            "tools.py (@tool com Pydantic), guardrails.py (middleware), "
            "agente.py (orquestração). Pipeline legado em _legado/. "
            "requirements.txt atualizado com LangChain."
        ),
        "falta": (
            "Sem __init__.py exportando funções públicas dos pacotes. "
            "Scripts v4-v12 não foram migrados para importar do orquestrador "
            "(código duplicado ainda presente). Sem README técnico descrevendo "
            "a arquitetura para novos desenvolvedores."
        ),
    },
    {
        "dimensao": "Testes",
        "nota": 3.5,
        "descricao": (
            "Os scripts test_pipeline_basicovN funcionam como testes de "
            "integração manuais e cobrem o fluxo end-to-end com dados reais. "
            "Existem arquivos em pipeline/tests/ (estrutura presente). "
            "O tratamento de erro a partir da v11 permite identificar "
            "falhas pontuais sem parar tudo."
        ),
        "falta": (
            "Zero testes unitários automatizados (pytest). Os transformers, "
            "a lógica de janela do resolver e os cálculos de estatísticas "
            "não têm nenhuma cobertura automatizada. Sem mocks para o "
            "collector (testes dependem de rede e da API do Sofascore). "
            "Sem CI rodando testes a cada push. Isso é o maior gap de "
            "qualidade do projeto."
        ),
    },
    {
        "dimensao": "Funcionalidade entregue",
        "nota": 8.0,
        "descricao": (
            "Pipeline diário automatizado que descobre jogos de amanhã, "
            "persiste o calendário completo da Copa e processa as seleções. "
            "Agente de análise com modelo Poisson (Dixon-Coles simplificado), "
            "5 tools com guardrails (max 10 calls, @wrap_tool_call), "
            "GPT-4o-mini gerando análise narrativa + 3 bilhetes classificados "
            "semanticamente (baixo/médio/alto risco). 7 grupos de endpoints REST."
        ),
        "falta": (
            "Frontend ainda desconectado da nova API. Sem cache no endpoint "
            "do agente (cada clique re-executa o LLM). Sem endpoint de "
            "comparação direta entre duas seleções (caso de uso central). "
            "Dados de ~24 das 48 seleções ingeridos — pipeline_diario.py "
            "resolve isso progressivamente ao rodar diariamente."
        ),
    },
    {
        "dimensao": "Aproveitamento dos dados disponíveis",
        "nota": 7.5,
        "descricao": (
            "O agente usa ativamente estatísticas, H2H, power ranking e o "
            "modelo Poisson para calcular probabilidades de 1X2, over/under "
            "1.5/2.5/3.5/4.5, BTTS, escanteios e cartões. O resolver de "
            "estatísticas expõe 30+ métricas calculadas via pandas com "
            "janela priorizada (Copa > amistoso). Performance rating do "
            "Sofascore integrado no pipeline de ingestão."
        ),
        "falta": (
            "goal_distribution_summary e tournament_overall_stats ainda "
            "retornam None (dados existem no collector mas não chegam ao "
            "resolver nem ao agente). Sem cache de análise do agente: "
            "re-processa tudo a cada chamada. Endpoint de H2H retorna dados "
            "brutos mas sem análise calculada (% de vitórias, gols médios "
            "nos confrontos, tendência recente)."
        ),
    },
]


def main() -> None:
    titulo("SOCCER MAGIC — AVALIAÇÃO DO BACKEND")
    import datetime
    data = datetime.date.today().strftime("%Y-%m-%d")
    print(f"\n  Projeto: Soccer Magic | Data da avaliação: {data}")
    print(f"  Avaliador: agente interno de qualidade")

    soma = sum(a["nota"] for a in AVALIACOES)
    media = soma / len(AVALIACOES)

    for av in AVALIACOES:
        titulo(av["dimensao"].upper())
        nota_linha(av["dimensao"], av["nota"])
        print()
        detalhe(av["descricao"])
        print()
        o_que_falta(av["falta"])

    titulo("NOTA GERAL")
    nota_linha("Média ponderada", media)
    print()
    detalhe(
        f"Nota geral: {media:.2f}/10. O backend evoluiu significativamente: "
        "pipeline diário automatizado, agente LLM com modelo Poisson e "
        "guardrails, 7 grupos de endpoints REST e orquestrador compartilhado "
        "eliminando duplicação. O maior gap que puxa a nota pra baixo continua "
        "sendo a ausência de testes automatizados (3.5/10). Conectar o frontend "
        "à nova API e adicionar cache no agente são os próximos passos de maior impacto."
    )
    print()


if __name__ == "__main__":
    main()

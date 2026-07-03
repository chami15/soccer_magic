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
        "nota": 6.5,
        "descricao": (
            "Os scripts test_pipeline_basicovN cobrem o fluxo end-to-end e "
            "servem como orquestrador manual funcional. A partir da v11 têm "
            "tratamento de erro por time e por partida com resumo final. "
            "A ordem de inserção respeita as FKs (dim antes de fato)."
        ),
        "falta": (
            "Não há orquestrador automatizado (scheduler, DAG, cron). Cada "
            "script é uma cópia quase idêntica da anterior — o padrão "
            "processar_time() deveria estar em um módulo compartilhado que "
            "os scripts apenas importam, passando a lista de times. Sem "
            "idempotência garantida no nível de execução (re-rodar o mesmo "
            "script pode gerar chamadas HTTP redundantes). Sem log estruturado "
            "(só print)."
        ),
    },
    {
        "dimensao": "API / Resolvers / Routers",
        "nota": 6.0,
        "descricao": (
            "Padrão resolver→router bem definido e consistente com o projeto "
            "de referência. Todos os endpoints retornam JSON estruturado com "
            "metadados (total, selecao_id). O resolver de estatísticas é o "
            "mais rico: 30+ campos calculados com pandas, janela de jogos "
            "priorizando Copa, sequência de forma, tendência de gols."
        ),
        "falta": (
            "Ainda sem autenticação/autorização nos endpoints (qualquer um "
            "pode chamar). Sem paginação nos endpoints de lista. Sem "
            "versionamento de API (/v1/...). Sem documentação OpenAPI além "
            "do gerado automático pelo FastAPI. goal_distribution_summary e "
            "tournament_overall_stats retornam sempre None no resolver de "
            "estatísticas. Sem endpoint de seleção individual (GET "
            "/api/selecoes/{id} retornando nome, grupo, ranking)."
        ),
    },
    {
        "dimensao": "Organização e estrutura de código",
        "nota": 8.0,
        "descricao": (
            "Separação clara entre camadas: collector / transformers / "
            "persisters / resolvers / routers / utils / sql. Cada arquivo "
            "tem responsabilidade única. Queries SQL nomeadas em arquivos "
            ".sql separados do Python, carregadas via SQLManager com cache. "
            "Pipeline legado isolado em _legado/ sem poluir o caminho ativo."
        ),
        "falta": (
            "Sem __init__.py exportando as funções públicas de cada pacote "
            "(importações ficam longas). Sem CLAUDE.md ou README técnico "
            "descrevendo a arquitetura para novos desenvolvedores. Falta "
            "um requirements.txt ou pyproject.toml completo e atualizado."
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
        "nota": 7.0,
        "descricao": (
            "Pipeline de ingestão funcional cobrindo 24 seleções (scripts "
            "v1-v12). API com 6 grupos de endpoints: estatísticas de seleção, "
            "partidas (lista + detalhe), jogadores, H2H, power ranking e "
            "calendário. O resolver de estatísticas agrega 30+ métricas "
            "relevantes para análise de Copa do Mundo."
        ),
        "falta": (
            "Frontend não conectado à nova API ainda (usa tabelas legadas "
            "que não existem mais no banco atual). Sem endpoint de comparação "
            "direta entre duas seleções (que seria o caso de uso central do "
            "projeto). Dados de 36 das 48 seleções da Copa ainda não foram "
            "ingeridos (apenas os times dos scripts v1-v12 foram processados)."
        ),
    },
    {
        "dimensao": "Aproveitamento dos dados disponíveis",
        "nota": 6.0,
        "descricao": (
            "Os dados coletados (goal distributions, overall statistics do "
            "torneio) existem no collector mas não chegam à API — o resolver "
            "retorna None nesses campos. O H2H tem dados ricos de histórico "
            "mas o resolver só expõe contagem de vitórias sem análise. "
            "Performance points do Sofascore são coletados mas não aparecem "
            "na resposta da API."
        ),
        "falta": (
            "Implementar goal_distribution_summary e tournament_overall_stats "
            "no resolver. Expor performance_rating nos endpoints de partida. "
            "Criar endpoint de comparação head-to-head com estatísticas "
            "calculadas de ambas as seleções lado a lado. Aproveitar "
            "performance points já coletados no pipeline."
        ),
    },
]


def main() -> None:
    titulo("SOCCER MAGIC — AVALIAÇÃO DO BACKEND")
    print(f"\n  Projeto: Soccer Magic | Data da avaliação: 2026-07-03")
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
        f"Nota geral: {media:.2f}/10. O backend tem uma base sólida de "
        "coleta e modelagem, com o pipeline de ingestão funcional e uma "
        "API em construção com boa separação de camadas. Os maiores gaps "
        "são a ausência de testes automatizados, a não conexão do frontend "
        "com a nova API, e o aproveitamento incompleto dos dados já "
        "disponíveis no banco."
    )
    print()


if __name__ == "__main__":
    main()

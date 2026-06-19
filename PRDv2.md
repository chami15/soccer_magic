# PRDv2 — Soccer Magic
**Documento de Requisitos de Produto — versão 2.0**
**Data:** 17/06/2026
**Autor:** Gustavo (ideação) + Claude (arquitetura e documentação)
**Status:** Rascunho em evolução — em ideação

---

## Índice

1. [Visão do produto](#1-visão-do-produto)
2. [Problema e oportunidade](#2-problema-e-oportunidade)
3. [Público-alvo](#3-público-alvo)
4. [Fonte de dados](#4-fonte-de-dados)
5. [Estatísticas cobertas](#5-estatísticas-cobertas)
6. [Funcionalidades do produto](#6-funcionalidades-do-produto)
7. [Pipeline de dados e lógica da janela deslizante](#7-pipeline-de-dados-e-lógica-da-janela-deslizante)
8. [Arquitetura técnica](#8-arquitetura-técnica)
9. [Design e experiência](#9-design-e-experiência)
10. [Roadmap e fases](#10-roadmap-e-fases)
11. [Premissas e limitações conhecidas](#11-premissas-e-limitações-conhecidas)
12. [Glossário](#12-glossário)
13. [Histórico de versões](#13-histórico-de-versões)

---

## 1. Visão do produto

**Soccer Magic** é uma plataforma web mobile first voltada para análise estatística das 48 seleções participantes da Copa do Mundo FIFA 2026. O produto entrega médias e indicadores calculados com base nos últimos 5 jogos de cada seleção, cobrindo tanto as partidas da Copa quanto amistosos recentes, sempre garantindo que o dado exibido reflete o estado mais atual de cada seleção.

> **Frase de posicionamento:**
> *"Estatísticas das seleções em disputa pela taça da Copa, baseadas em dados confiáveis, visando ótimas decisões."*

A proposta central é oferecer dados rigorosamente corretos, com uma identidade visual premium e dark, para suportar análises esportivas e tomadas de decisão em apostas — posicionando o Soccer Magic como ferramenta séria de inteligência analítica, não apenas um placar.

**Princípio inegociável:** um dado errado na plataforma é pior do que nenhum dado. Toda a arquitetura do pipeline é orientada a garantir que os 5 jogos exibidos sejam sempre os mais relevantes e recentes — com prioridade absoluta para partidas da Copa 2026.

---

## 2. Problema e oportunidade

Plataformas como 365Scores, SofaScore e WhoScored oferecem dados estatísticos ricos, mas apresentam limitações importantes para o público de analistas e apostadores focados na Copa 2026:

- Os dados não são filtrados para os últimos N jogos por seleção de forma simples
- Não há visão comparativa direta entre duas seleções em formato adequado para apostas
- A experiência mobile é poluída por anúncios e fluxos de navegação não otimizados para pesquisa analítica
- Nenhuma delas combina em uma tela única: médias dos últimos 5 jogos + histórico de resultados + comparativo direto entre times
- Nenhuma é construída exclusivamente para o contexto da Copa, com a janela de análise centrada no torneio

**Oportunidade:** Criar uma experiência enxuta, com identidade visual premium dark, focada exclusivamente nas 48 seleções da Copa 2026, com dados calculados sobre uma janela deslizante de 5 jogos com garantia absoluta de que jogos da Copa sempre entram na análise, e com funcionalidade de simulação de confronto lado a lado.

---

## 3. Público-alvo

### Primário
**Analistas esportivos e apostadores** — pessoas que usam dados para embasar apostas em mercados como Over/Under de gols, escanteios, cartões, ambas marcam, e resultados.

Perfil: familiaridade com plataformas de odds (Bet365, Betano, Sportingbet), habituados a cruzar estatísticas de múltiplas fontes antes de apostar, acessam o produto majoritariamente pelo celular.

### Secundário
**Entusiastas de futebol** — torcedores que acompanham a Copa e querem entender o desempenho das seleções além do placar, mas sem interesse em apostas.

---

## 4. Fonte de dados

### API primária: API-Football (api-sports.io)

| Atributo | Detalhe |
|---|---|
| Provedor | API-Sports (api-football.com) |
| Cobertura Copa 2026 | `league=1`, `season=2026` — 48 times, 104 partidas |
| Cobertura amistosos | `league=10` (International Friendlies) |
| Endpoint de estatísticas | `GET /fixtures/statistics?fixture={id}` |
| Endpoint de partidas por time | `GET /fixtures?team={id}&last=10` |
| Frequência de atualização | A cada 1 minuto durante partidas ao vivo |
| Plano recomendado | Pro ($19/mês) — sem limite diário restritivo |
| Tier free | 100 requests/dia — suficiente para prototipagem |

### Endpoints utilizados no pipeline

```
GET /fixtures?team={team_id}&last=10           → últimas 10 partidas do time
GET /fixtures/statistics?fixture={fixture_id}  → estatísticas detalhadas de cada partida
GET /fixtures/players?fixture={fixture_id}     → stats por jogador por partida
GET /teams?league=1&season=2026                → lista dos 48 times da Copa
```

### Política de coleta

- O pipeline coleta sempre os **10 jogos mais recentes** de cada seleção a cada execução
- A seleção dos 5 jogos que compõem a janela segue a **lógica de prioridade da Copa** descrita em detalhes na seção 7
- O campo `match_type` de cada jogo é armazenado para exibição na interface (`Copa` ou `Amistoso`)
- A janela é **sempre reconstruída do zero** a cada execução — nunca incremental — eliminando edge cases de estado inconsistente

---

## 5. Estatísticas cobertas

### 5.1 Estatísticas disponíveis via API-Football (`/fixtures/statistics`)

Estas são retornadas diretamente e calculadas como **média por jogo** ao longo dos últimos 5:

| Campo na API | Métrica exibida | Relevância para apostas |
|---|---|---|
| `Shots on Goal` | Chutes ao gol / jogo | Alta — mercado de total de finalizações |
| `Shots off Goal` | Chutes fora / jogo | Média |
| `Total Shots` | Total de chutes / jogo | Alta |
| `Shots insidebox` | Chutes dentro da área / jogo | Alta — indica pressão real |
| `Shots outsidebox` | Chutes fora da área / jogo | Baixa |
| `Blocked Shots` | Chutes bloqueados / jogo | Média |
| `Corner Kicks` | Escanteios / jogo | Muito alta — mercado dedicado |
| `Fouls` | Faltas cometidas / jogo | Alta — cartões e pênaltis |
| `Offsides` | Impedimentos / jogo | Média |
| `Ball Possession` | Posse de bola média (%) | Alta — indica estilo de jogo |
| `Yellow Cards` | Cartões amarelos / jogo | Muito alta — mercado de cartões |
| `Red Cards` | Cartões vermelhos / jogo | Alta |
| `Goalkeeper Saves` | Defesas do goleiro / jogo | Alta — indica pressão sofrida |
| `Total passes` | Passes totais / jogo | Média |
| `Passes accurate` | Passes certos / jogo | Média |
| `Passes %` | Precisão de passes (%) | Alta — qualidade de construção |

### 5.2 Estatísticas adicionais (via livescore-api — integração v1.1)

Disponíveis em API complementar e altamente relevantes para apostas:

| Campo | Métrica exibida | Fonte | Relevância |
|---|---|---|---|
| `throw_ins` | Laterais / jogo | livescore-api.com | Média — pressão territorial |
| `goal_kicks` | Tiros de meta / jogo | livescore-api.com | Média — fase defensiva |
| `free_kicks` | Cobranças de falta / jogo | livescore-api.com | Alta — potencial de gol |
| `dangerous_attacks` | Ataques perigosos / jogo | livescore-api.com | Muito alta — pressão ofensiva real |
| `attacks` | Ataques totais / jogo | livescore-api.com | Alta |

> **Nota de implementação:** Na v1.0, priorizamos os campos da seção 5.1 (API-Football). Os campos da 5.2 entram como melhoria na v1.1 via livescore-api.com.

### 5.3 Métricas derivadas por jogador (via `/fixtures/players`)

Calculadas a partir do endpoint de estatísticas por jogador, agrupadas por time e normalizadas por jogo:

| Métrica | Fórmula | Relevância |
|---|---|---|
| Passes / jogador / jogo | `total_passes / players_used / games` | Intensidade de circulação |
| Chutes / jogador / jogo | `total_shots / players_used / games` | Agressividade ofensiva |
| Faltas / jogador / jogo | `total_fouls / players_used / games` | Tendência disciplinar individual |
| Cartões / jogador / jogo | `total_cards / players_used / games` | Risco disciplinar por jogador |
| Duelos ganhos (%) | `duels_won / duels_total` | Intensidade física |

> Métricas por jogador ficam em seção colapsável na ficha da seleção — não no nível de KPI principal.

### 5.4 Indicadores calculados (calculados no pipeline, não vêm da API)

| Indicador | Fórmula | Relevância para apostas |
|---|---|---|
| Média de gols marcados / jogo | `goals_scored / 5` | Mercado Over/Under |
| Média de gols sofridos / jogo | `goals_conceded / 5` | Mercado ambas marcam |
| Clean sheets nos últimos 5 | Contagem de jogos sem gol sofrido | Mercado under + ambas marcam |
| Taxa de jogos com +1.5 gols | % de partidas com 2+ gols | Mercado Over 1.5 |
| Taxa de jogos com +2.5 gols | % de partidas com 3+ gols | Mercado Over 2.5 |
| Taxa de jogos com +3.5 escanteios | % de partidas com 4+ escanteios | Mercado escanteios |
| Taxa BTTS (ambas marcam) | % de partidas em que ambos os times marcaram | Mercado BTTS |
| Gols no 1º tempo / jogo | `first_half_goals / 5` | Mercado 1º tempo |
| Gols no 2º tempo / jogo | `second_half_goals / 5` | Mercado 2º tempo |
| Forma recente | Sequência V/E/D dos últimos 5 jogos | Contexto geral |
| Tendência ofensiva | Média de gols dos últimos 3 vs 5 jogos | Momento da seleção |

---

## 6. Funcionalidades do produto

### 6.1 Tela inicial — Lista de seleções por grupo

- Exibe as 48 seleções organizadas por grupo (A a L)
- Card por seleção com: bandeira, nome, forma recente (V/E/D), e acesso à ficha
- Campo de busca rápida por nome da seleção
- Indicador visual de quando os dados foram atualizados pela última vez
- Filtro opcional: ordenar por média de gols, escanteios ou cartões

**Dados exibidos no card de lista:**
- Bandeira e nome da seleção
- Forma: sequência visual dos últimos 5 (ex: V V E D V)
- Destaque de 1 KPI configurável (gols, escanteios ou cartões/jogo)
- Badge indicando quantos dos 5 jogos são da Copa (ex: "2 Copa · 3 Amistosos")

---

### 6.2 Ficha da seleção — Tela de estatísticas detalhadas

Acessada ao tocar no card de qualquer seleção. Exibe todos os indicadores calculados sobre os últimos 5 jogos.

#### Seção 1 — KPIs principais (grid 2×3)

| KPI | Descrição |
|---|---|
| Gols marcados / jogo | Média ofensiva geral |
| Gols sofridos / jogo | Média defensiva geral |
| Escanteios / jogo | Média de corners |
| Cartões / jogo | Soma de amarelos e vermelhos |
| Chutes ao gol / jogo | Precisão ofensiva |
| Posse de bola (%) | Estilo de jogo predominante |

#### Seção 2 — Indicadores de apostas

| Indicador | Visual |
|---|---|
| Clean sheets / 5 jogos | Badge numérico |
| Taxa Over 1.5 | Barra de progresso % |
| Taxa Over 2.5 | Barra de progresso % |
| Taxa BTTS | Barra de progresso % |
| Taxa Over 3.5 escanteios | Barra de progresso % |
| Gols 1º tempo / jogo | Número |
| Gols 2º tempo / jogo | Número |

#### Seção 3 — Estatísticas completas (lista colapsável)

Todas as métricas brutas médias: faltas, passes totais, precisão de passes, chutes bloqueados, chutes dentro/fora da área, impedimentos, defesas do goleiro, laterais, tiros de meta, cobranças de falta, ataques perigosos.

#### Seção 4 — Histórico dos últimos 5 jogos

Por jogo: adversário, placar, data, tipo (badge `Copa` ou `Amistoso`), placares por tempo.

#### Seção 5 — Médias por jogador (colapsável)

Top 5 jogadores com mais minutos nos últimos 5 jogos: passes, chutes e faltas por jogo.

---

### 6.3 Simule seu jogo — Comparativo direto entre duas seleções

Funcionalidade acessada pela aba "Simular" na navegação principal.

**Fluxo:**
1. Usuário seleciona Seleção A (dropdown com busca)
2. Usuário seleciona Seleção B (dropdown com busca)
3. Sistema exibe visão comparativa lado a lado

**Categorias comparadas:**

| Categoria | Métricas |
|---|---|
| Ofensivo | Gols/jogo, Chutes/jogo, Chutes ao gol/jogo, Ataques perigosos/jogo |
| Defensivo | Gols sofridos/jogo, Clean sheets, Defesas/jogo |
| Disciplinar | Cartões/jogo, Faltas/jogo |
| Territorial | Escanteios/jogo, Posse (%), Passes/jogo |
| Apostas | Over 1.5 %, Over 2.5 %, BTTS %, Over 3.5 escanteios % |

**Elementos visuais:**
- Barra dupla: time A (roxo neon) vs time B (branco/cinza), valores em cada extremidade
- Destaque no lado com vantagem em cada métrica
- Resumo de vantagens: "Brasil lidera em 6 de 12 categorias"
- Forma recente de cada time lado a lado
- Badge de composição da janela: quantos dos 5 jogos são da Copa para cada time

---

### 6.4 Atualização de dados (pipeline on-demand)

- Botão "Atualizar dados" visível na interface (restrito a operador/admin)
- Exibe timestamp da última atualização em todas as telas
- Exibe log resumido do último ciclo: "48 seleções processadas · 3 janelas alteradas · 0 erros"
- A janela de cada seleção é reconstruída do zero a cada execução

---

## 7. Pipeline de dados e lógica da janela deslizante

Esta seção é o coração da integridade do produto. Toda a confiabilidade dos dados exibidos depende da lógica descrita aqui ser implementada sem desvios.

### 7.1 Princípio fundamental

> **A janela dos 5 jogos é sempre reconstruída do zero a cada execução do pipeline. Não há estado incremental — o pipeline nunca "adiciona um jogo ao topo" da janela. Ele sempre recalcula quais são os 5 jogos corretos com base nos dados mais recentes da API.**

Isso garante que:
- Um jogo da Copa recém-disputado **sempre** entra na janela
- Nunca há risco de um jogo da Copa ficar de fora por ter sido processado em ordem errada
- Dados corrompidos ou incompletos de uma execução anterior são sobrescritos na próxima

---

### 7.2 Algoritmo de seleção dos 5 jogos (especificação completa)

O algoritmo é executado por seleção, a cada ciclo do pipeline.

```
ENTRADA:
  - team_id: identificador da seleção
  - matches_raw: lista dos 10 jogos mais recentes da API
    (filtrados por status FT = Full Time — apenas partidas encerradas)

PASSO 1 — Separar por tipo
  copa_matches    = [m para m em matches_raw se m.league_id == 1]
                    ordenados por data DESC (mais recente primeiro)
  friendly_matches = [m para m em matches_raw se m.league_id == 10]
                    ordenados por data DESC (mais recente primeiro)

PASSO 2 — Construir a janela
  window = []

  // Jogos da Copa entram TODOS primeiro, até o limite de 5
  para cada jogo em copa_matches:
    se len(window) < 5:
      window.append(jogo)

  // Amistosos completam a janela apenas se houver espaço
  para cada jogo em friendly_matches:
    se len(window) < 5:
      window.append(jogo)

PASSO 3 — Validação de integridade
  se len(window) < 3:
    LOGAR ALERTA: "Seleção {team_id} tem menos de 3 jogos disponíveis — dados insuficientes"
    MARCAR seleção como insuficiente no banco (campo data_quality = 'insufficient')
    NÃO calcular médias — exibir aviso na interface

  se len(window) >= 3 e len(window) < 5:
    LOGAR AVISO: "Seleção {team_id} tem apenas {len(window)} jogos — médias calculadas sobre janela parcial"
    MARCAR seleção com data_quality = 'partial'

  se len(window) == 5:
    MARCAR seleção com data_quality = 'complete'

SAÍDA:
  window: lista ordenada de até 5 jogos (Copa primeiro, depois amistosos)
  data_quality: 'complete' | 'partial' | 'insufficient'
  copa_count: quantidade de jogos da Copa na janela
  friendly_count: quantidade de amistosos na janela
```

---

### 7.3 Comportamento por cenário de jogo da Copa

Estes são todos os cenários possíveis durante o torneio, com o comportamento esperado:

| Cenário | Copa na janela | Amistosos na janela | Novo jogo da Copa | Resultado após atualização |
|---|---|---|---|---|
| Início da Copa (1ª rodada) | 0 | 5 | 1 | **Copa entra, amistoso mais antigo sai → 1 Copa + 4 amistosos** |
| Após 2ª rodada | 1 | 4 | 1 | **Copa entra, amistoso mais antigo sai → 2 Copa + 3 amistosos** |
| Após 3ª rodada (fase de grupos) | 2 | 3 | 1 | **Copa entra, amistoso mais antigo sai → 3 Copa + 2 amistosos** |
| Oitavas de final | 3 | 2 | 1 | **Copa entra, amistoso mais antigo sai → 4 Copa + 1 amistoso** |
| Quartas de final | 4 | 1 | 1 | **Copa entra, amistoso mais antigo sai → 5 Copa + 0 amistosos** |
| Semifinal e além | 5 | 0 | 1 | **Copa entra, Copa mais antiga sai → janela toda Copa** |
| Rodada dupla¹ | 2 | 3 | 2 | **Ambas as Copas entram, 2 amistosos saem → 4 Copa + 1 amistoso** |

> ¹ Não ocorre na fase de grupos (uma partida por rodada), mas pode ocorrer se o pipeline não for executado entre rodadas consecutivas.

**Regra derivada crítica:** amistosos são **removidos** da janela conforme novos jogos da Copa acontecem. Um amistoso nunca "empurra" um jogo da Copa para fora. Matematicamente: `copa_matches` sempre preenche a janela antes de `friendly_matches`.

---

### 7.4 O que acontece com jogos que a API ainda não finalizou

O pipeline filtra apenas partidas com `fixture.status.short == "FT"` (Full Time). Partidas em andamento, suspensas ou abandonadas são ignoradas. Isso garante que estatísticas de jogos incompletos nunca contaminam as médias.

```python
# Filtro obrigatório antes de qualquer seleção
matches_raw = [
    m for m in api_response
    if m['fixture']['status']['short'] == 'FT'
]
```

---

### 7.5 Fluxo completo do pipeline

```
[TRIGGER]
  Manual via botão na interface (operador)
  Futuro v1.1: cron diário às 06h00 (horário de Brasília)
        ↓
[COLETA — API-Football]
  GET /teams?league=1&season=2026
  → Obtém lista atualizada das 48 seleções com seus IDs
        ↓
  Para cada seleção:
  GET /fixtures?team={id}&last=10&status=FT
  → Retorna até 10 partidas encerradas mais recentes
        ↓
[ALGORITMO DE JANELA]
  Aplica o algoritmo da seção 7.2 para cada seleção
  Determina quais 5 fixture_ids compõem a janela
  Define data_quality, copa_count, friendly_count
        ↓
[COLETA DE ESTATÍSTICAS]
  Para cada fixture_id na janela de cada seleção:
  GET /fixtures/statistics?fixture={id}
  GET /fixtures/players?fixture={id}
  GET /fixtures/events?fixture={id}  ← para gols por tempo (1H / 2H)
        ↓
[TRANSFORMAÇÃO]
  Calcular médias por jogo para cada métrica
  Calcular indicadores derivados (Over%, BTTS%, Clean sheets)
  Calcular gols por tempo via eventos
  Calcular forma recente (V/E/D sequência)
  Calcular tendência (média últimos 3 vs média dos 5)
  Tratar campos null: COALESCE(valor, 0) com flag de ausência
        ↓
[PERSISTÊNCIA — Supabase]
  Upsert na tabela team_stats (por team_id)
  Upsert na tabela match_log (por fixture_id)
  Atualizar pipeline_runs com timestamp, seleções processadas e erros
        ↓
[RESPOSTA PARA INTERFACE]
  Retorna JSON com: seleções processadas, janelas alteradas,
  alertas de qualidade, timestamp, erros encontrados
```

---

### 7.6 Estimativa de requests por ciclo completo

| Operação | Requests |
|---|---|
| Listar 48 times da Copa | 1 |
| Buscar últimas 10 partidas de cada time | 48 |
| Buscar estatísticas de 5 fixtures por time | 48 × 5 = 240 |
| Buscar stats de jogadores por fixture | 48 × 5 = 240 |
| Buscar eventos por fixture (gols por tempo) | 48 × 5 = 240 |
| **Total por ciclo completo** | **~769 requests** |

> Com o plano Pro da API-Football (7.500 requests/dia), um ciclo completo consome ~10% da cota diária. É possível rodar múltiplas vezes ao dia sem risco de limitação.

---

## 8. Arquitetura técnica

### 8.1 Stack definida

| Camada | Tecnologia | Justificativa |
|---|---|---|
| **Pipeline** | Python 3.11+ | Ecossistema maduro para ETL, pandas para transformação |
| **Banco de dados** | Supabase (PostgreSQL) | Managed, client JS nativo, RLS, free tier generoso |
| **Frontend** | Next.js 14 (App Router) | SSR/SSG para mobile em conexões lentas, rotas nativas |
| **Estilização** | Tailwind CSS | Utilitários mobile first, dark mode nativo via `dark:` |
| **Gráficos** | Recharts | Touch-friendly, integração React nativa, licença MIT |
| **Deploy frontend** | Vercel | Integração automática com Next.js, CDN global |
| **Pipeline hospedagem** | Local (v1.0) / Railway ou Render (v1.1) | Script Python disparado manualmente na v1.0 |

### 8.2 Schema do banco de dados

```sql
-- Seleções participantes
CREATE TABLE teams (
  id           INTEGER PRIMARY KEY,  -- ID API-Football
  name         TEXT NOT NULL,
  country      TEXT,
  flag_url     TEXT,
  group_name   TEXT,                 -- Grupo A..L
  updated_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Estatísticas agregadas (últimos 5 jogos)
CREATE TABLE team_stats (
  team_id              INTEGER PRIMARY KEY REFERENCES teams(id),

  -- Composição da janela
  copa_count           INTEGER NOT NULL DEFAULT 0,      -- 0 a 5: jogos da Copa na janela
  friendly_count       INTEGER NOT NULL DEFAULT 0,      -- 0 a 5: amistosos na janela
  data_quality         TEXT NOT NULL DEFAULT 'complete',-- 'complete' | 'partial' | 'insufficient'
  games_window         JSONB,                           -- array com os 5 fixture_ids usados

  -- Médias ofensivas
  avg_goals_scored     NUMERIC(4,2),
  avg_goals_conceded   NUMERIC(4,2),
  avg_shots_total      NUMERIC(4,2),
  avg_shots_on_goal    NUMERIC(4,2),
  avg_shots_inside_box NUMERIC(4,2),
  avg_shots_outside_box NUMERIC(4,2),
  avg_blocked_shots    NUMERIC(4,2),

  -- Médias territoriais
  avg_corners          NUMERIC(4,2),
  avg_possession       NUMERIC(5,2),   -- %
  avg_passes_total     NUMERIC(6,2),
  avg_passes_accurate  NUMERIC(6,2),
  avg_passes_pct       NUMERIC(5,2),   -- %
  avg_offsides         NUMERIC(4,2),

  -- Médias disciplinares
  avg_fouls            NUMERIC(4,2),
  avg_yellow_cards     NUMERIC(4,2),
  avg_red_cards        NUMERIC(4,2),

  -- Médias defensivas
  avg_saves            NUMERIC(4,2),

  -- Indicadores derivados
  clean_sheets         INTEGER,        -- contagem (0-5)
  over15_pct           NUMERIC(5,2),   -- % de jogos com +1.5 gols (total)
  over25_pct           NUMERIC(5,2),
  over35_pct           NUMERIC(5,2),
  btts_pct             NUMERIC(5,2),
  over35_corners_pct   NUMERIC(5,2),
  avg_goals_1h         NUMERIC(4,2),
  avg_goals_2h         NUMERIC(4,2),

  -- Forma e tendência
  form_sequence        TEXT,           -- ex: "V V E D V"
  trend_goals_3v5      NUMERIC(4,2),   -- diff média gols (3 vs 5 jogos)

  -- Metadados
  updated_at           TIMESTAMPTZ DEFAULT NOW()
);

-- Log de partidas (raw, para auditoria e recálculo)
CREATE TABLE match_log (
  fixture_id      INTEGER PRIMARY KEY,
  team_id         INTEGER REFERENCES teams(id),
  opponent_name   TEXT,
  date            DATE,
  league_id       INTEGER,
  league_name     TEXT,
  match_type      TEXT CHECK (match_type IN ('Copa', 'Amistoso')),
  score_home      INTEGER,
  score_away      INTEGER,
  score_ht_home   INTEGER,
  score_ht_away   INTEGER,
  is_in_window    BOOLEAN DEFAULT FALSE,  -- true = está nos 5 jogos ativos da seleção
  stats_raw       JSONB,                  -- resposta bruta da API
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Log de execuções do pipeline
CREATE TABLE pipeline_runs (
  id                  SERIAL PRIMARY KEY,
  started_at          TIMESTAMPTZ NOT NULL,
  finished_at         TIMESTAMPTZ,
  teams_processed     INTEGER DEFAULT 0,
  windows_changed     INTEGER DEFAULT 0,  -- seleções com janela diferente da anterior
  errors_count        INTEGER DEFAULT 0,
  error_log           JSONB,
  triggered_by        TEXT DEFAULT 'manual'  -- 'manual' | 'cron'
);
```

---

## 9. Design e experiência

### 9.1 Princípios de design

- **Dark first:** a interface é projetada nativamente para dark mode — não é uma versão adaptada. O fundo escuro reduz fadiga visual em sessões longas de análise
- **Premium e focado:** visual limpo, sem anúncios, sem ruído — cada elemento na tela tem uma razão de estar lá
- **Roxo neon como linguagem de destaque:** o neon roxo sinaliza o que importa — KPIs em destaque, valores superiores no comparativo, elementos interativos
- **Dados antes de decoração:** KPIs em destaque imediato, sem banners, sem distrações
- **Confiança visual:** badges de qualidade de dados (composição da janela Copa/Amistoso) dão transparência ao usuário sobre o que está sendo calculado

### 9.2 Identidade visual — Soccer Magic

| Elemento | Valor | Uso |
|---|---|---|
| **Background principal** | `#0A0A0F` | Fundo das telas |
| **Background de superfície** | `#111118` | Cards, modais, bottom nav |
| **Background elevado** | `#1A1A24` | KPI cards, inputs, hover |
| **Roxo neon** | `#A855F7` | Destaque principal — CTAs, KPIs em foco, barra ativa |
| **Roxo neon claro** | `#C084FC` | Textos de destaque secundário, labels |
| **Roxo neon escuro** | `#7C3AED` | Bordas de cards selecionados, fills |
| **Roxo neon glow** | `#A855F7` com `box-shadow: 0 0 12px #A855F720` | Efeito neon em cards de KPI |
| **Branco principal** | `#F8FAFC` | Textos primários |
| **Cinza médio** | `#94A3B8` | Textos secundários, labels |
| **Cinza escuro** | `#334155` | Bordas sutis, separadores |
| **Verde vitória** | `#22C55E` | Resultado V, clean sheets, vantagem |
| **Amarelo empate** | `#EAB308` | Resultado E, cartões amarelos |
| **Vermelho derrota** | `#EF4444` | Resultado D, cartões vermelhos, déficit |
| **Âmbar indicador** | `#F59E0B` | KPIs neutros em destaque |
| **Tipografia** | Inter (Google Fonts) | Excelente legibilidade em telas pequenas |
| **Fonte de dados** | Mono espaçada — `JetBrains Mono` | Valores numéricos (KPIs, placares) |

### 9.3 Aplicação visual dos elementos neon

```
Cards de KPI:
  background: #1A1A24
  border: 1px solid #7C3AED40
  border-top: 2px solid #A855F7
  box-shadow: 0 0 16px #A855F715

Valor numérico em destaque (KPI principal):
  color: #A855F7
  font-family: JetBrains Mono
  font-size: 28px

Barra de progresso (Over%, BTTS%):
  track: #1A1A24
  fill: linear #7C3AED → #A855F7
  glow: box-shadow 0 0 8px #A855F740

Navegação ativa (bottom nav):
  icon + label: color #A855F7
  indicator: underline 2px solid #A855F7

Badge "Copa":
  background: #7C3AED20
  color: #C084FC
  border: 1px solid #7C3AED60

Badge "Amistoso":
  background: #334155
  color: #94A3B8
```

### 9.4 Estrutura de navegação (mobile)

```
Bottom Navigation Bar (fixa — background #111118, border-top #334155)
├── 🏠 Seleções    → Lista por grupo
├── ⚽ Simular     → Confronto comparativo
└── 🔄 Pipeline    → Status + botão de atualização (admin)
```

### 9.5 Hierarquia de informação na ficha da seleção

```
[Header]
  Bandeira + Nome + Grupo + Badge composição da janela
  Forma recente (pills V/E/D com cores semânticas)
        ↓
[Grid KPIs] — 6 cards neon
  Gols marcados · Gols sofridos
  Escanteios · Cartões
  Chutes ao gol · Posse %
        ↓
[Indicadores de apostas]
  Over 1.5 | Over 2.5 | BTTS | Over 3.5 cant.
  (barras de progresso roxo neon)
        ↓
[Histórico dos 5 jogos]
  Timeline com placares, badges Copa/Amistoso
        ↓
[Estatísticas completas] — colapsável
  Todas as médias brutas em lista
        ↓
[Por jogador] — colapsável
  Top 5 por minutos jogados
```

---

## 10. Roadmap e fases

### Fase 1 — MVP (v1.0)

**Objetivo:** Produto funcional com dados reais das 48 seleções, visual dark neon e as três telas principais.

| Item | Descrição |
|---|---|
| Pipeline Python | Coleta, algoritmo de janela, transformação e persistência no Supabase |
| Banco de dados | Schema Supabase completo conforme seção 8.2 |
| Identidade visual | Dark mode com roxo neon implementado via Tailwind + CSS custom |
| Tela: lista de seleções | Por grupos, cards com KPI, forma e badge de composição |
| Tela: ficha da seleção | KPIs neon, indicadores de apostas, histórico, stats completas |
| Tela: simule seu jogo | Comparativo com barras duplas roxo vs cinza |
| Tela: pipeline | Status, timestamp, log do último ciclo, botão atualizar |

### Fase 2 — Evolução (v1.1)

| Item | Descrição |
|---|---|
| Métricas por jogador | Expandir seção de stats por jogador na ficha |
| Laterais e tiros de meta | Integrar dados da livescore-api (seção 5.2) |
| Sparklines | Mini gráfico de linha de gols e escanteios nas 5 partidas |
| Filtros na lista | Ordenação por gols, escanteios, cartões |
| Cron automático | Job diário automático via Railway/Render |

### Fase 3 — Expansão (v2.0)

| Item | Descrição |
|---|---|
| Head-to-head histórico | Últimos confrontos entre as seleções no Simule seu jogo |
| Compartilhamento | URL única por confronto simulado |
| Exportação | Download do comparativo em imagem (WhatsApp / Telegram) |
| PWA | Instalação como app no celular (manifest + service worker) |
| Notificações | Push quando nova partida é processada |

---

## 11. Premissas e limitações conhecidas

| Premissa / Limitação | Impacto | Mitigação |
|---|---|---|
| API-Football pode não ter `throw_ins` e `goal_kicks` no endpoint v3 | Métricas da seção 5.2 ausentes na v1 | Integrar livescore-api na v1.1 |
| Amistosos de baixa relevância podem distorcer médias | Dados menos representativos no início do torneio | Badge na interface mostra composição da janela; usuário tem contexto |
| Pipeline manual depende de operador | Dados podem ficar desatualizados se operador não executar | Automatizar na v1.1 com cron |
| API-Football pode ter indisponibilidade pontual | Pipeline falha silenciosamente | Retry com exponential backoff; log de erros na tabela `pipeline_runs` |
| Free tier (100 req/dia) não suporta ciclo completo | Limitação na prototipagem | Testar com 5–10 seleções no free, subir para Pro ($19/mês) na produção |
| Campos `null` em amistosos menos cobertos | Médias incompletas | `COALESCE(valor, 0)` na transformação; flag de ausência por campo |
| Seleção eliminada na fase de grupos terá janela estagnada | Dados congelados após eliminação | Marcar seleção como "eliminada" no banco; exibir badge na interface |

---

## 12. Glossário

| Termo | Definição |
|---|---|
| **Sliding window** | Janela deslizante de 5 jogos reconstruída do zero a cada ciclo do pipeline |
| **KPI** | Key Performance Indicator — indicador chave de desempenho |
| **BTTS** | Both Teams to Score — mercado de apostas onde ambas as equipes marcam |
| **Over X.5** | Mercado de apostas onde o total de gols/escanteios/etc supera X.5 |
| **Clean sheet** | Partida em que o time não sofreu gols |
| **xG** | Expected Goals — gols esperados com base nas finalizações (não incluso na v1) |
| **Pipeline ETL** | Extract, Transform, Load — processo de coleta, transformação e carga de dados |
| **Upsert** | Operação de banco que insere se não existe ou atualiza se já existe |
| **league_id=1** | Identificador da Copa do Mundo FIFA na API-Football |
| **league_id=10** | Identificador de amistosos internacionais na API-Football |
| **data_quality** | Campo que sinaliza se a janela tem 5 jogos completos, parcial (3–4) ou insuficiente (<3) |
| **copa_count** | Quantidade de jogos da Copa presente na janela ativa da seleção |
| **FT** | Full Time — status de partida encerrada na API-Football |
| **Neon roxo** | Cor de destaque `#A855F7` — identidade visual do Soccer Magic |

---

## 13. Histórico de versões

| Versão | Data | Autor | Alterações |
|---|---|---|---|
| v1.0 | 17/06/2026 | Gustavo + Claude | Documento inicial — visão, dados, funcionalidades, arquitetura e roadmap |
| v2.0 | 17/06/2026 | Gustavo + Claude | Renomeação para Soccer Magic; nova identidade visual dark + roxo neon; algoritmo de sliding window completamente reescrito com garantia de prioridade Copa; novos campos no schema (`copa_count`, `friendly_count`, `data_quality`, `is_in_window`, tabela `pipeline_runs`); seção 7 inteiramente nova com algoritmo formal, tabela de cenários e pseudocódigo; frase de posicionamento atualizada |

---

*Próxima revisão planejada: após validação do algoritmo de janela com dados reais da API-Football e definição do design system em Tailwind.*

# SPECv2.md — Soccer Magic
**Especificação Técnica — v2.0**
**Data:** 18/06/2026
**Produto:** Soccer Magic — Plataforma de análise estatística das 48 seleções da Copa do Mundo FIFA 2026
**Implementação:** Claude Code (terminal VS Code)

---

## Changelog v1 → v2

| Área | Mudança |
|---|---|
| **Fonte de dados** | API-Football removida. Substituída por web scraping da API interna do Sofascore |
| **Responsividade** | Expandida de mobile-first para totalmente responsiva (mobile / tablet / desktop) |
| **Schema** | `fixture_id` renomeado para `match_id`; `league_id` → `tournament_id` para refletir nomenclatura Sofascore |
| **Pipeline** | `collector.py` reescrito; dependências atualizadas (httpx + playwright) |
| **Roadmap** | Removida referência à livescore-api (substituída pelo Sofascore) |

---

## ⚠️ LEITURA OBRIGATÓRIA ANTES DE QUALQUER IMPLEMENTAÇÃO

Esta especificação é o guia técnico canônico do Soccer Magic. O [PRDv2.md](./PRDv2.md) define o "o quê" e o "por quê". Este SPECv2 define o "como".

**Dois princípios inegociáveis:**
1. **Dados corretos acima de tudo** — um dado errado é pior que nenhum dado
2. **Trabalho em equipe de agentes** — toda implementação usa os agentes da pasta `AGENTS/`

---

## 1. PROTOCOLO OBRIGATÓRIO DE AGENTES

> **Claude do terminal do VS Code: você DEVE usar os agentes da pasta `AGENTS/` para implementar este projeto. Nenhuma fase pode ser implementada sem o agente correspondente ativo.**

A pasta `AGENTS/` contém 6 subagentes especializados que trabalham em equipe:

| Arquivo | Quando ativar |
|---|---|
| `AGENTS/soccer-orchestrator.md` | **Sempre primeiro** — coordena todas as fases e agentes |
| `AGENTS/soccer-database-architect.md` | Fase 1: criar schema Supabase via MCP |
| `AGENTS/soccer-pipeline-engineer.md` | Fase 2: implementar pipeline Python (scraping Sofascore) |
| `AGENTS/soccer-data-validator.md` | Após cada fase: validar integridade dos dados |
| `AGENTS/soccer-frontend-developer.md` | Fase 3: implementar frontend Next.js responsivo |
| `AGENTS/soccer-qa-engineer.md` | Após cada módulo: testes e qualidade |

### Ordem de execução obrigatória

```
FASE 1 — Infraestrutura
  [soccer-orchestrator] coordena:
    1. [soccer-database-architect] → criar schema no Supabase via MCP
    2. [soccer-data-validator]     → verificar 4 tabelas criadas corretamente
    ✅ Checkpoint: tabelas teams, team_stats, match_log, pipeline_runs existem

FASE 2 — Pipeline Python (Sofascore scraping)
  [soccer-orchestrator] coordena:
    1. [soccer-pipeline-engineer] → implementar pipeline completo
    2. [soccer-qa-engineer]       → testes de window.py e transformer.py
    3. [soccer-data-validator]    → validar 7 cenários §7.3 do PRDv2
    ✅ Checkpoint: pipeline roda com ≥1 seleção real, dados no Supabase

FASE 3 — Frontend Responsivo
  [soccer-orchestrator] coordena:
    1. [soccer-frontend-developer] → implementar 4 telas (mobile + tablet + desktop)
    2. [soccer-qa-engineer]        → validar responsividade e dados→UI
    ✅ Checkpoint: localhost:3000 exibe dados reais em 375px, 768px e 1280px

FASE 4 — Integração final
  [soccer-orchestrator] coordena:
    1. Pipeline completo (48 seleções via Sofascore)
    2. [soccer-data-validator] → auditoria de 5 seleções
    3. [soccer-qa-engineer]    → checklist final
    ✅ Produto pronto
```

### Como ativar um agente

```bash
# No terminal do VS Code com Claude Code:
claude --agent AGENTS/soccer-orchestrator.md

# Ou mencionar o agente diretamente na conversa:
# "Use o agente soccer-pipeline-engineer para implementar o collector.py"
```

---

## 2. STACK E AMBIENTE

### Tecnologias

| Camada | Tecnologia | Versão mínima |
|---|---|---|
| Pipeline | Python | 3.11+ |
| Scraping (primário) | httpx | 0.27+ |
| Scraping (fallback) | Playwright (Python) | 1.44+ |
| Frontend | Next.js (App Router) | 14.x |
| Estilização | Tailwind CSS | 3.x |
| Gráficos | Recharts | 2.x |
| Banco de dados | Supabase (PostgreSQL) | — |
| Deploy frontend | Vercel | — |

### Variáveis de ambiente

**`pipeline/.env`** (nunca commitar — incluir no .gitignore):
```bash
SUPABASE_URL=<url do projeto Supabase>
SUPABASE_SERVICE_KEY=<service_role key — não usar anon key no pipeline>
```

**`.env.local`** (Next.js — nunca commitar):
```bash
NEXT_PUBLIC_SUPABASE_URL=<url do projeto Supabase>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon key — leitura pública>
```

> Não há mais chave de API externa. O pipeline scrapa o Sofascore diretamente.

### Supabase — regra crítica

> **TODA operação no Supabase DEVE usar as ferramentas MCP do Supabase.**
> Nunca usar `psql` no terminal, nunca rodar `.sql` via Bash diretamente.

Ferramentas MCP obrigatórias:
- `apply_migration` → criar/alterar schema
- `execute_sql` → consultas e verificações
- `list_tables` → confirmar estrutura existente
- `generate_typescript_types` → gerar tipos após mudanças de schema

---

## 3. ESTRUTURA DE PASTAS

```
Soccer_Magic/
├── PRDv2.md                       ← documento de produto (referência)
├── SPECv2.md                      ← este arquivo (canônico)
├── AGENTS/                        ← subagentes especializados (usar obrigatoriamente)
│   ├── soccer-orchestrator.md
│   ├── soccer-pipeline-engineer.md
│   ├── soccer-database-architect.md
│   ├── soccer-frontend-developer.md
│   ├── soccer-data-validator.md
│   └── soccer-qa-engineer.md
│
├── pipeline/                      ← ETL Python (scraping Sofascore)
│   ├── main.py                    ← orquestrador: collector → window → transformer → persistence
│   ├── collector.py               ← scraping da API interna do Sofascore
│   ├── window.py                  ← algoritmo sliding window §7.2 (isolado e testável)
│   ├── transformer.py             ← cálculo de médias, derivados, forma, tendência
│   ├── persistence.py             ← upserts no Supabase via supabase-py
│   ├── requirements.txt
│   └── tests/
│       ├── __init__.py
│       ├── test_window.py         ← 100% cobertura dos 7 cenários §7.3
│       ├── test_transformer.py    ← fórmulas de médias e indicadores
│       └── fixtures/              ← mocks de respostas do Sofascore
│
├── app/                           ← Next.js 14 App Router
│   ├── layout.tsx                 ← RootLayout: fontes, nav responsiva
│   ├── (main)/
│   │   ├── page.tsx               ← /  Lista de seleções por grupo
│   │   ├── teams/[id]/page.tsx    ← /teams/[id] Ficha da seleção
│   │   ├── simulate/page.tsx      ← /simulate Comparativo
│   │   └── pipeline/page.tsx      ← /pipeline Status e log
│   └── api/
│       └── pipeline/route.ts      ← POST → dispara pipeline Python
│
├── components/
│   ├── ui/
│   │   ├── KpiCard.tsx
│   │   ├── FormBadge.tsx
│   │   ├── WindowBadge.tsx
│   │   ├── ProgressBar.tsx
│   │   └── DoubleBar.tsx
│   ├── TeamCard.tsx
│   ├── TeamStats.tsx
│   ├── MatchHistory.tsx
│   ├── SimulateView.tsx
│   ├── PipelineStatus.tsx
│   ├── BottomNav.tsx              ← mobile + tablet
│   └── SideNav.tsx                ← desktop (lg:)
│
├── lib/
│   ├── supabase.ts                ← createServerClient + createBrowserClient
│   ├── types.ts                   ← tipos de domínio
│   └── database.types.ts          ← gerado pelo MCP Supabase
│
├── supabase/
│   └── migrations/
│       └── 001_initial.sql        ← schema completo (referência; aplicar via MCP)
│
├── tailwind.config.ts
├── next.config.ts
├── package.json
└── .gitignore                     ← incluir: .env, .env.local, pipeline/.env
```

---

## 4. SCHEMA DO BANCO DE DADOS

> Aplicar via MCP `apply_migration`. Nunca via terminal SQL.

```sql
-- =====================================================
-- TEAMS: seleções participantes
-- =====================================================
CREATE TABLE IF NOT EXISTS teams (
  id           INTEGER PRIMARY KEY,  -- ID Sofascore do time
  name         TEXT NOT NULL,
  country      TEXT,
  flag_url     TEXT,                 -- URL da bandeira (Sofascore CDN ou emoji fallback)
  group_name   TEXT,                 -- 'A' a 'L'
  updated_at   TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- TEAM_STATS: estatísticas agregadas (janela 5 jogos)
-- =====================================================
CREATE TABLE IF NOT EXISTS team_stats (
  team_id              INTEGER PRIMARY KEY REFERENCES teams(id),

  -- Composição da janela
  copa_count           INTEGER NOT NULL DEFAULT 0,      -- jogos da Copa na janela (0-5)
  friendly_count       INTEGER NOT NULL DEFAULT 0,      -- amistosos na janela (0-5)
  data_quality         TEXT NOT NULL DEFAULT 'complete'
                         CHECK (data_quality IN ('complete','partial','insufficient')),
  games_window         JSONB,  -- array de match_ids na janela ativa

  -- Médias ofensivas
  avg_goals_scored      NUMERIC(4,2),
  avg_goals_conceded    NUMERIC(4,2),
  avg_shots_total       NUMERIC(4,2),
  avg_shots_on_goal     NUMERIC(4,2),
  avg_shots_inside_box  NUMERIC(4,2),
  avg_shots_outside_box NUMERIC(4,2),
  avg_blocked_shots     NUMERIC(4,2),

  -- Médias territoriais
  avg_corners           NUMERIC(4,2),
  avg_possession        NUMERIC(5,2),  -- percentual (ex: 58.30)
  avg_passes_total      NUMERIC(6,2),
  avg_passes_accurate   NUMERIC(6,2),
  avg_passes_pct        NUMERIC(5,2),  -- percentual
  avg_offsides          NUMERIC(4,2),

  -- Médias disciplinares
  avg_fouls             NUMERIC(4,2),
  avg_yellow_cards      NUMERIC(4,2),
  avg_red_cards         NUMERIC(4,2),

  -- Médias defensivas
  avg_saves             NUMERIC(4,2),

  -- Indicadores derivados
  clean_sheets          INTEGER,        -- contagem 0-5
  over15_pct            NUMERIC(5,2),
  over25_pct            NUMERIC(5,2),
  over35_pct            NUMERIC(5,2),
  btts_pct              NUMERIC(5,2),
  over35_corners_pct    NUMERIC(5,2),
  avg_goals_1h          NUMERIC(4,2),
  avg_goals_2h          NUMERIC(4,2),

  -- Forma e tendência
  form_sequence         TEXT,           -- "V V E D V"
  trend_goals_3v5       NUMERIC(4,2),   -- avg(3 jogos) - avg(5 jogos)

  updated_at            TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- MATCH_LOG: partidas raw (auditoria e recálculo)
-- =====================================================
CREATE TABLE IF NOT EXISTS match_log (
  match_id        INTEGER PRIMARY KEY,    -- ID do evento no Sofascore
  team_id         INTEGER REFERENCES teams(id),
  opponent_name   TEXT,
  date            DATE,
  tournament_id   INTEGER,               -- ID do torneio no Sofascore
  tournament_name TEXT,
  match_type      TEXT CHECK (match_type IN ('Copa','Amistoso')),
  score_home      INTEGER,
  score_away      INTEGER,
  score_ht_home   INTEGER,
  score_ht_away   INTEGER,
  is_in_window    BOOLEAN DEFAULT FALSE,
  stats_raw       JSONB,                  -- resposta bruta do Sofascore /statistics
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- PIPELINE_RUNS: log de execuções do pipeline
-- =====================================================
CREATE TABLE IF NOT EXISTS pipeline_runs (
  id               SERIAL PRIMARY KEY,
  started_at       TIMESTAMPTZ NOT NULL,
  finished_at      TIMESTAMPTZ,
  teams_processed  INTEGER DEFAULT 0,
  windows_changed  INTEGER DEFAULT 0,
  errors_count     INTEGER DEFAULT 0,
  error_log        JSONB,
  triggered_by     TEXT DEFAULT 'manual'
                     CHECK (triggered_by IN ('manual','cron'))
);

-- =====================================================
-- ÍNDICES DE PERFORMANCE
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_match_log_team_id      ON match_log(team_id);
CREATE INDEX IF NOT EXISTS idx_match_log_is_in_window ON match_log(is_in_window) WHERE is_in_window = TRUE;
CREATE INDEX IF NOT EXISTS idx_teams_group_name        ON teams(group_name);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started   ON pipeline_runs(started_at DESC);

-- =====================================================
-- RLS (Row Level Security)
-- =====================================================
ALTER TABLE teams          ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_stats     ENABLE ROW LEVEL SECURITY;
ALTER TABLE match_log      ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_runs  ENABLE ROW LEVEL SECURITY;

-- Leitura pública (anon + authenticated)
CREATE POLICY "public_read_teams"         ON teams         FOR SELECT USING (true);
CREATE POLICY "public_read_team_stats"    ON team_stats    FOR SELECT USING (true);
CREATE POLICY "public_read_match_log"     ON match_log     FOR SELECT USING (true);
CREATE POLICY "public_read_pipeline_runs" ON pipeline_runs FOR SELECT USING (true);
-- Escrita: apenas via service_role key (pipeline Python), que bypassa RLS
```

---

## 5. PIPELINE PYTHON — SOFASCORE SCRAPING

> **Fonte de dados:** API interna do Sofascore (`https://api.sofascore.com/api/v1/`)
> Implementado pelo agente `soccer-pipeline-engineer`.

### 5.1 Abordagem de scraping

O Sofascore expõe uma API JSON interna que alimenta seu próprio site. Ela é acessível via HTTP com headers de navegador simulados — sem necessidade de renderização JavaScript para os dados que precisamos.

**Estratégia em duas camadas:**
- **Primária:** `httpx` (async HTTP) com headers que simulam navegador Chrome
- **Fallback:** `Playwright` (browser headless) caso o Sofascore retorne 403 ou dados vazios

### 5.2 Endpoints da API interna do Sofascore

```
BASE_URL = "https://api.sofascore.com/api/v1"

Headers obrigatórios (simular Chrome):
  User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36
  Accept: application/json, text/plain, */*
  Accept-Language: pt-BR,pt;q=0.9,en;q=0.8
  Referer: https://www.sofascore.com/
  Origin: https://www.sofascore.com

Endpoints utilizados:
  GET /unique-tournament/{wc_tournament_id}/seasons
    → listar seasons para identificar o ID da season 2026

  GET /unique-tournament/{wc_tournament_id}/season/{season_id}/teams
    → 48 seleções com IDs Sofascore, nomes e bandeiras

  GET /team/{team_id}/events/last/{page}
    → página de eventos recentes (page=0 → 10 mais recentes)
    → filtrar: status.type == 'finished' (equivalente ao FT)

  GET /event/{event_id}/statistics
    → estatísticas da partida (shots, corners, possession, etc.)

  GET /event/{event_id}/incidents
    → incidentes: gols (com período), cartões, substituições

  GET /event/{event_id}/lineups
    → jogadores utilizados (para seção por jogador)
```

### 5.3 Identificação dos IDs do Sofascore

No primeiro ciclo do pipeline, descobrir dinamicamente:

```python
# Sofascore IDs (a confirmar na primeira execução inspecionando as respostas)
WC_2026_TOURNAMENT_ID = 16    # FIFA World Cup — tournament ID no Sofascore
                               # Confirmar acessando: sofascore.com/pt/copa-do-mundo/
                               # e inspecionando chamadas de rede no DevTools

# ID da season 2026 — descoberto dinamicamente:
def get_wc_2026_season_id(tournament_id: int) -> int:
    seasons = httpx.get(f"{BASE_URL}/unique-tournament/{tournament_id}/seasons")
    for season in seasons.json()['seasons']:
        if season['year'] == 2026:
            return season['id']
    raise ValueError("Season 2026 da Copa não encontrada no Sofascore")

# Amistosos internacionais — identificar pelo tournament.uniqueTournament.id
# que NÃO é o WC_2026_TOURNAMENT_ID. Qualquer partida internacional com
# status.type == 'finished' que não seja Copa é tratada como amistoso.
```

### 5.4 Mapeamento de campos Sofascore → schema

```python
# Partida (de /team/{id}/events/last/0)
match = {
    "match_id":       event['id'],
    "tournament_id":  event['tournament']['uniqueTournament']['id'],
    "tournament_name": event['tournament']['uniqueTournament']['name'],
    "match_type":     'Copa' if event['tournament']['uniqueTournament']['id'] == WC_2026_TOURNAMENT_ID else 'Amistoso',
    "date":           datetime.fromtimestamp(event['startTimestamp']).date(),
    "score_home":     event['homeScore']['current'],
    "score_away":     event['awayScore']['current'],
    "score_ht_home":  event['homeScore'].get('period1', None),
    "score_ht_away":  event['awayScore'].get('period1', None),
}

# Filtro de partida encerrada:
is_finished = event['status']['type'] == 'finished'

# Estatísticas (de /event/{id}/statistics → groups[].statisticsItems)
# Mapeamento dos nomes no Sofascore → colunas do banco:
STATS_MAP = {
    "Ball possession":          "avg_possession",
    "Total shots":              "avg_shots_total",
    "Shots on target":          "avg_shots_on_goal",
    "Blocked shots":            "avg_blocked_shots",
    "Shots inside box":         "avg_shots_inside_box",
    "Shots outside box":        "avg_shots_outside_box",
    "Corner kicks":             "avg_corners",
    "Offsides":                 "avg_offsides",
    "Fouls":                    "avg_fouls",
    "Yellow cards":             "avg_yellow_cards",
    "Red cards":                "avg_red_cards",
    "Goalkeeper saves":         "avg_saves",
    "Total passes":             "avg_passes_total",
    "Accurate passes":          "avg_passes_accurate",
    "Accurate passes %":        "avg_passes_pct",
}

# Gols por tempo (de /event/{id}/incidents)
# Filtrar: incidentType == 'goal' (não 'ownGoal' para o atacante, mas contar tudo no placar)
# period: 1 → 1º tempo, 2 → 2º tempo
goals_1h = [i for i in incidents if i['incidentType'] == 'goal' and i['period'] == 1 and time_marcou(i, team_id)]
goals_2h = [i for i in incidents if i['incidentType'] == 'goal' and i['period'] == 2 and time_marcou(i, team_id)]
```

### 5.5 Rate limiting e robustez

```python
# Entre cada request
time.sleep(1.5)   # Sofascore é mais restritivo que APIs pagas

# Retry com backoff exponencial: 3 tentativas em 2s, 4s, 8s
# Se 3 falhas consecutivas: logar como erro, pular seleção, continuar

# Fallback Playwright (apenas se httpx retornar 403 repetidamente):
# Usar browser headless para navegar até a página da partida e extrair o JSON
# do window.__INITIAL_DATA__ ou das chamadas de rede interceptadas
```

### 5.6 Algoritmo de janela deslizante (§7.2 do PRDv2) — inalterado

> **Este algoritmo é o coração do produto. A mudança de fonte de dados não altera sua lógica.**

```
ENTRADA: matches_raw (apenas status.type == 'finished', ordenados por data DESC)

PASSO 1 — Separar por tipo:
  copa_matches     = [m para m em matches_raw se m.tournament_id == WC_2026_TOURNAMENT_ID]
  friendly_matches = [m para m em matches_raw se m.tournament_id != WC_2026_TOURNAMENT_ID]
  (ambos ordenados por data DESC)

PASSO 2 — Copa entra PRIMEIRO:
  window = []
  para cada jogo em copa_matches:     se len(window) < 5: window.append(jogo)
  para cada jogo em friendly_matches: se len(window) < 5: window.append(jogo)

PASSO 3 — Validar qualidade:
  len < 3  → data_quality = 'insufficient' (não calcular médias)
  3–4      → data_quality = 'partial'
  5        → data_quality = 'complete'

SAÍDA: window, data_quality, copa_count, friendly_count
```

**Cenários válidos (tabela §7.3 do PRDv2):**

| Situação | Copa na entrada | Resultado esperado |
|---|---|---|
| Início da Copa | 1 Copa + N amistosos | 1 Copa + 4 Amistosos |
| Após 2ª rodada | 2 Copa + N amistosos | 2 Copa + 3 Amistosos |
| Após 3ª rodada | 3 Copa + N amistosos | 3 Copa + 2 Amistosos |
| Oitavas | 4 Copa + N amistosos | 4 Copa + 1 Amistoso |
| Quartas+ | 5+ Copa | 5 Copa + 0 Amistosos |
| Rodada dupla | 2 novas Copa | Copa priorizada corretamente |

### 5.7 Fórmulas de transformação

```python
n = len(window)  # divisor REAL: pode ser 3, 4 ou 5 — nunca fixar em 5

# Gols
avg_goals_scored   = sum(gols_do_time_em_cada_jogo) / n
avg_goals_conceded = sum(gols_sofridos_em_cada_jogo) / n

# Indicadores derivados
over15_pct         = count(jogos onde total_gols >= 2) / n * 100
over25_pct         = count(jogos onde total_gols >= 3) / n * 100
over35_pct         = count(jogos onde total_gols >= 4) / n * 100
btts_pct           = count(jogos onde gols_casa>0 AND gols_fora>0) / n * 100
over35_corners_pct = count(jogos onde corners >= 4) / n * 100

# Gols por tempo via incidents
avg_goals_1h = sum(gols_do_time em period=1) / n
avg_goals_2h = sum(gols_do_time em period=2) / n

# Forma
form_sequence = ' '.join(['V'|'E'|'D' para cada jogo na window, do ponto de vista do time])

# Tendência
trend_goals_3v5 = round(avg(gols em window[:3]) - avg_goals_scored, 2)

# COALESCE: campos None/ausentes → 0 no banco; nunca propagar None
def coalesce(val): return val if val is not None else 0
```

### 5.8 Dependências (`requirements.txt`)

```
httpx==0.27.0
playwright==1.44.0
supabase==2.3.0
python-dotenv==1.0.0
pytest==7.4.0
pytest-cov==4.1.0
```

---

## 6. FRONTEND NEXT.JS 14 — RESPONSIVO

> Implementado pelo agente `soccer-frontend-developer`.

### 6.1 Princípio de responsividade

O Soccer Magic deve oferecer **ótima experiência em todas as plataformas**:

| Breakpoint | Largura | Layout de navegação | Grid de seleções |
|---|---|---|---|
| Mobile | < 768px | BottomNav (fixa) | 1 coluna |
| Tablet | 768px–1023px | BottomNav (fixa) | 2 colunas |
| Desktop | ≥ 1024px | SideNav (lateral esquerda, 240px) | 3 colunas |

### 6.2 Design tokens (tailwind.config.ts)

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          base:     '#0A0A0F',
          surface:  '#111118',
          elevated: '#1A1A24',
        },
        neon: {
          DEFAULT: '#A855F7',
          light:   '#C084FC',
          dark:    '#7C3AED',
        },
        text: {
          primary:   '#F8FAFC',
          secondary: '#94A3B8',
          border:    '#334155',
        },
        semantic: {
          win:   '#22C55E',
          draw:  '#EAB308',
          loss:  '#EF4444',
          amber: '#F59E0B',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        neon:      '0 0 16px #A855F715',
        'neon-sm': '0 0 8px #A855F740',
      },
    },
  },
}
export default config
```

### 6.3 Layout raiz responsivo (`app/layout.tsx`)

```tsx
// Mobile/tablet: padding-bottom para BottomNav
// Desktop (lg:): padding-left para SideNav (240px)
<body className="bg-bg-base min-h-screen pb-16 lg:pb-0 lg:pl-60">
  <SideNav />     {/* hidden md:hidden lg:flex — lateral no desktop */}
  <BottomNav />   {/* flex lg:hidden — bottom em mobile/tablet */}
  <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    {children}
  </main>
</body>
```

### 6.4 Telas e rotas

| Rota | Componente principal | Dados do Supabase |
|---|---|---|
| `/` | Lista de seleções por grupo | `teams` JOIN `team_stats` ORDER BY group_name, name |
| `/teams/[id]` | Ficha completa | `team_stats` WHERE team_id=:id + `match_log` WHERE is_in_window=true |
| `/simulate` | Comparativo A vs B | `team_stats` para dois times |
| `/pipeline` | Status e log | `pipeline_runs` ORDER BY started_at DESC LIMIT 10 |

### 6.5 Componentes responsivos por tela

#### Tela 1: Lista de seleções (`/`)
```
Mobile:  1 coluna de cards, grupo como header de seção
Tablet:  2 colunas de cards por grupo
Desktop: 3 colunas + sidebar de filtros (ordenar por KPI)

TeamCard (por breakpoint):
  Mobile:  bandeira | nome + forma | KPI à direita
  Tablet:  mesmo layout, card mais largo
  Desktop: card expandido com 2 KPIs visíveis
```

#### Tela 2: Ficha da seleção (`/teams/[id]`)
```
Header (todos): bandeira + nome + grupo + WindowBadge + FormSequence

KPI Grid:
  Mobile:  2×3 (2 colunas, 3 linhas)
  Tablet:  3×2 (3 colunas, 2 linhas)
  Desktop: 6×1 (6 colunas, 1 linha) — sem scroll horizontal

Indicadores de apostas:
  Mobile/Tablet: lista vertical (ProgressBar em full width)
  Desktop: 2 colunas de ProgressBars lado a lado

Histórico de jogos:
  Mobile:  cards verticais empilhados
  Tablet:  tabela compacta (3 colunas)
  Desktop: tabela completa (todas as colunas visíveis)
```

#### Tela 3: Simule seu jogo (`/simulate`)
```
Mobile:  seleção A (topo) → vs → seleção B (abaixo) → DoubleBar full width
Tablet:  idem, mas DoubleBar com mais espaço
Desktop: dois painéis lado a lado (seleção A | seleção B) com DoubleBar centralizada
         Resumo de liderança sempre visível no topo
```

#### Tela 4: Pipeline (`/pipeline`)
```
Mobile/Tablet: cards verticais com métricas + botão atualizar
Desktop: tabela de execuções com mais colunas + status em tempo real
```

### 6.6 Componentes UI — especificação

```tsx
// KpiCard — sem alteração visual, mas responsivo em tamanho
// Mobile: font-size do valor = 28px | Desktop: 32px

// DoubleBar — responsivo
// Mobile: barras empilhadas verticalmente (A em cima, B embaixo)
// Desktop: barras horizontais lado a lado

// SideNav (desktop apenas)
// bg-bg-surface, border-right border-text-border/30
// Largura: 240px fixo
// Itens: Seleções / Simular / Pipeline (com ícones)
// Logo "Soccer Magic" no topo com cor neon

// BottomNav (mobile + tablet)
// bg-bg-surface, border-top border-text-border
// hidden em lg:
```

### 6.7 Comportamentos críticos (todos os breakpoints)

- `data_quality === 'insufficient'` → exibir aviso em vez de KPIs (em qualquer tamanho de tela)
- `data_quality === 'partial'` → KPIs + banner "Médias sobre N jogos"
- Valores `null` no banco → exibir `—` (nunca `0` artificial)
- Todos os valores numéricos em `font-mono`
- Loading: skeleton `animate-pulse bg-elevated` proporcional ao layout do breakpoint atual
- Sem scroll horizontal em qualquer breakpoint

### 6.8 Supabase no frontend

```typescript
// lib/supabase.ts
import { createServerClient, createBrowserClient } from '@supabase/ssr'

export function createSupabaseServer() {
  // Server Components e Route Handlers
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { /* next/headers */ } }
  )
}

export function createSupabaseBrowser() {
  // Client Components ('use client')
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

---

## 7. INTEGRIDADE DOS DADOS — REGRAS INVIOLÁVEIS

### Regras do pipeline

1. **Janela sempre do zero** — nunca incremental; reconstruir a cada ciclo
2. **Somente partidas encerradas** — filtrar `status.type == 'finished'` antes de qualquer lógica
3. **Copa sempre primeiro** — `copa_matches` preenche `window[]` antes de amistosos
4. **Divisor real** — médias divididas por `len(window)`, nunca por `5` fixo
5. **COALESCE obrigatório** — campos ausentes/None do Sofascore → `0` no banco
6. **Falha individual não aborta** — erro em 1 seleção → logar e continuar para a próxima

### Regras da UI

7. **`insufficient` → sem KPIs** — exibir aviso em vez de zeros enganosos
8. **WindowBadge obrigatório** — em toda tela que exibe estatísticas
9. **Zero recálculo no frontend** — exibir exatamente o que veio do banco
10. **Arredondamento consistente** — `NUMERIC(4,2)` no banco → 2 casas decimais na UI

### Validação pós-pipeline (obrigatória)

O agente `soccer-data-validator` deve executar após cada ciclo:
- 3 seleções aleatórias: `avg_goals_scored` do banco vs soma manual do `match_log`
- Tolerância: `±0.01`
- Desvio acima disso → **bloquear uso da UI até investigação**

---

## 8. API ROUTE — TRIGGER DO PIPELINE

```typescript
// app/api/pipeline/route.ts
import { NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export async function POST() {
  try {
    const { stdout } = await execAsync('python pipeline/main.py', {
      cwd: process.cwd(),
      env: { ...process.env },
      timeout: 300_000   // 5 min timeout para 48 seleções
    })
    return NextResponse.json({ success: true, log: stdout })
  } catch (error) {
    return NextResponse.json({ success: false, error: String(error) }, { status: 500 })
  }
}
```

> Para produção (v1.1): substituir `exec` por job queue (Railway cron ou Render).

---

## 9. VERIFICAÇÃO END-TO-END

Execute na ordem após implementar todas as fases:

```bash
# 1. Schema Supabase (via MCP execute_sql)
SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;
# → match_log, pipeline_runs, team_stats, teams

# 2. Instalar dependências do pipeline
cd pipeline
pip install -r requirements.txt
playwright install chromium   # instalar browser para fallback

# 3. Rodar testes unitários
pytest tests/ -v --cov=window --cov=transformer --cov-report=term-missing
# → 0 failures; window.py coverage = 100%

# 4. Rodar pipeline com 2 seleções de teste
python main.py --limit 2
# → "2 seleções processadas · X janelas alteradas · 0 erros"

# 5. Confirmar dados no Supabase (via MCP execute_sql)
SELECT team_id, copa_count, friendly_count, data_quality, avg_goals_scored
FROM team_stats LIMIT 5;

# 6. Iniciar frontend
npm run dev    # localhost:3000

# 7. Testar responsividade (DevTools do browser)
# → 375px: layout mobile correto, sem scroll horizontal
# → 768px: 2 colunas de cards, bottom nav visível
# → 1280px: sidebar visível, 3 colunas, bottom nav oculto

# 8. Verificar ficha de uma seleção
# → KPIs batem com banco; WindowBadge correto

# 9. Testar simulador
# → selecionar 2 times; barras duplas com valores corretos

# 10. Tela pipeline → clicar "Atualizar dados"
# → log aparece com timestamp e contagens
```

---

## 10. ROADMAP TÉCNICO

### v1.1
- Cron automático via Railway/Render (`triggered_by = 'cron'`)
- Sparklines com Recharts na ficha (mini gráfico gols e escanteios)
- Coluna `eliminated_at` em `teams` para seleções eliminadas
- Filtros e ordenação na lista (por gols, escanteios, cartões)

### v2.0
- Head-to-head histórico entre seleções no Simulador
- PWA (manifest + service worker)
- Compartilhamento via URL única por confronto simulado
- Exportação do comparativo como imagem (WhatsApp / Telegram)

---

## 11. REFERÊNCIAS

- [PRDv2.md](./PRDv2.md) — documento de produto
- [AGENTS/soccer-orchestrator.md](./AGENTS/soccer-orchestrator.md) — ponto de entrada obrigatório
- Sofascore web: `https://www.sofascore.com/pt/copa-do-mundo/`
- Supabase JS docs: `https://supabase.com/docs/reference/javascript`
- Next.js App Router: `https://nextjs.org/docs/app`
- Playwright Python: `https://playwright.dev/python/`

---

*SPECv2 — Soccer Magic. Implementação pelo Claude Code no terminal do VS Code usando os agentes da pasta `AGENTS/`.*

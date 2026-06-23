-- =====================================================
-- Soccer Magic — Banco v3 (modelo estrela)
-- Construído incrementalmente: cada tabela é discutida e
-- aprovada antes de ser adicionada aqui.
-- =====================================================

-- ---------------------------------------------------
-- DIM_SELECAO
-- Dimensão: atributos da seleção que mudam pouco/raramente.
-- Substitui a tabela "teams" atual, com o ranking FIFA a mais.
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_selecao (
  id            INTEGER PRIMARY KEY,   -- ID Sofascore do time
  nome          TEXT NOT NULL,
  continente    TEXT,
  grupo         TEXT,                  -- 'A' a 'L'
  ranking_fifa  INTEGER,                -- posição atual no ranking FIFA
  atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------
-- DIM_JOGADOR
-- Dimensão: atributos do jogador, vistos nos incidentes
-- (gols/assistências) e no passing network do Sofascore.
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_jogador (
  id              INTEGER PRIMARY KEY,   -- ID Sofascore do jogador
  nome            TEXT NOT NULL,
  nome_curto      TEXT,                  -- ex: "Vinícius Jr."
  posicao         TEXT,                  -- 'F', 'M', 'D', 'G'
  numero_camisa   TEXT,
  valor_mercado   NUMERIC(12,2),
  moeda           TEXT,                  -- ex: 'EUR'
  selecao_id      INTEGER REFERENCES dim_selecao(id),
  atualizado_em   TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------
-- FATO_PARTIDA
-- Fato: 1 linha por jogo (passado ou futuro/agendado).
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS fato_partida (
  id              INTEGER PRIMARY KEY,   -- ID Sofascore do evento
  custom_id       TEXT,                  -- slug usado em /event/{customId}/h2h/events
  selecao_home_id INTEGER NOT NULL REFERENCES dim_selecao(id),
  selecao_away_id INTEGER NOT NULL REFERENCES dim_selecao(id),
  placar_home     INTEGER,
  placar_away     INTEGER,
  placar_ht_home  INTEGER,
  placar_ht_away  INTEGER,
  status          TEXT,                  -- 'notstarted' | 'inprogress' | 'finished'
  vencedor_id     INTEGER REFERENCES dim_selecao(id),  -- NULL se empate ou nao terminou
  tipo            TEXT,                  -- 'Copa' | 'Amistoso'
  grupo           TEXT,                  -- ex: 'Group I' (fase de grupos)
  rodada          INTEGER,
  data_partida    DATE,
  cidade          TEXT,
  atualizado_em   TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------
-- FATO_ESTATISTICA_SELECAO_PARTIDA
-- Fato: 1 linha por seleção por partida — estatísticas
-- granulares (substitui o calculo de medias direto no
-- pipeline Python; agora a media da janela pode ser uma
-- VIEW/query sobre esta tabela).
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS fato_estatistica_selecao_partida (
  partida_id          INTEGER NOT NULL REFERENCES fato_partida(id),
  selecao_id           INTEGER NOT NULL REFERENCES dim_selecao(id),
  resultado             CHAR(1) CHECK (resultado IN ('V', 'E', 'D')),
  gols_marcados          INTEGER,
  gols_sofridos          INTEGER,
  posse_bola            NUMERIC(5,2),
  chutes_total           INTEGER,
  chutes_no_gol          INTEGER,
  chutes_bloqueados      INTEGER,
  chutes_dentro_area     INTEGER,
  chutes_fora_area       INTEGER,
  escanteios             INTEGER,
  impedimentos           INTEGER,
  faltas                 INTEGER,
  cartoes_amarelos       INTEGER,
  cartoes_vermelhos      INTEGER,
  defesas                INTEGER,
  passes_total           INTEGER,
  passes_certos          INTEGER,
  passes_precisao_pct    NUMERIC(5,2),
  gols_1_tempo           INTEGER,
  gols_2_tempo           INTEGER,
  performance_rating     NUMERIC(4,2),  -- nota de desempenho do Sofascore na partida
  PRIMARY KEY (partida_id, selecao_id)
);

-- ---------------------------------------------------
-- FATO_EVENTO_PARTIDA
-- Fato: 1 linha por evento granular da partida (gol,
-- cartao, substituicao) — com jogador, assistencia e minuto.
-- jogador_id é reaproveitado: jogador que marcou (gol) ou que
-- recebeu o cartao (cartao_amarelo/vermelho). Em substituicao,
-- usar jogador_saida_id/jogador_entrada_id em vez de jogador_id.
-- Coordenadas de chute/passing network (footballPassingNetworkAction)
-- ficaram fora por granularidade/complexidade alta para o MVP —
-- avaliar no futuro como JSONB opcional se for necessario.
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS fato_evento_partida (
  id              INTEGER PRIMARY KEY,    -- ID Sofascore do incidente
  partida_id      INTEGER NOT NULL REFERENCES fato_partida(id),
  selecao_id      INTEGER NOT NULL REFERENCES dim_selecao(id),
  tipo_evento     TEXT NOT NULL,          -- 'gol' | 'cartao_amarelo' | 'cartao_vermelho' | 'substituicao'
  minuto          INTEGER NOT NULL,
  minuto_extra     INTEGER,                -- tempo de acrescimo, quando houver
  jogador_id      INTEGER REFERENCES dim_jogador(id),
  assistencia_jogador_id INTEGER REFERENCES dim_jogador(id),
  jogador_saida_id       INTEGER REFERENCES dim_jogador(id),  -- p/ substituicao
  jogador_entrada_id     INTEGER REFERENCES dim_jogador(id),  -- p/ substituicao
  tipo_gol        TEXT,                   -- 'regular' | 'penalty' | 'own-goal' | etc.
  var_decisao     TEXT,                   -- ex: 'goal_awarded' | 'goal_disallowed', quando houve revisao VAR
  criado_em       TIMESTAMPTZ DEFAULT NOW()
);

-- ---------------------------------------------------
-- PIPELINE_RUNS
-- Log de execucoes do pipeline (igual ao schema atual).
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS pipeline_runs (
  id               SERIAL PRIMARY KEY,
  started_at       TIMESTAMPTZ NOT NULL,
  finished_at      TIMESTAMPTZ,
  teams_processed  INTEGER DEFAULT 0,
  windows_changed  INTEGER DEFAULT 0,
  errors_count     INTEGER DEFAULT 0,
  error_log        JSONB,
  triggered_by     TEXT DEFAULT 'manual'
                     CHECK (triggered_by IN ('manual', 'cron'))
);

-- ---------------------------------------------------
-- FATO_H2H_EVENTO
-- Fato: 1 linha por confronto direto historico entre duas
-- selecoes, vindo de /event/{customId}/h2h/events — escopo
-- mais amplo que fato_partida (cobre jogos de outros torneios
-- e anos anteriores, nao só a janela atual da Copa).
-- ---------------------------------------------------
CREATE TABLE IF NOT EXISTS fato_h2h_evento (
  id              INTEGER PRIMARY KEY,   -- ID Sofascore do evento
  selecao_a_id    INTEGER NOT NULL REFERENCES dim_selecao(id),
  selecao_b_id    INTEGER NOT NULL REFERENCES dim_selecao(id),
  placar_a        INTEGER,
  placar_b        INTEGER,
  vencedor_id     INTEGER REFERENCES dim_selecao(id),  -- NULL se empate
  torneio_nome    TEXT,
  data_partida    DATE,
  performance_a   NUMERIC(4,2),  -- nota de desempenho do Sofascore da selecao_a nesse confronto
  performance_b   NUMERIC(4,2),  -- nota de desempenho do Sofascore da selecao_b nesse confronto
  criado_em       TIMESTAMPTZ DEFAULT NOW()
);

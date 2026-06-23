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

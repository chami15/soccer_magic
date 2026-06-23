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
  id                  INTEGER PRIMARY KEY,   -- ID Sofascore do jogador
  nome                TEXT NOT NULL,
  nome_curto          TEXT,                  -- ex: "Vinícius Jr."
  posicao             TEXT,                  -- 'F', 'M', 'D', 'G'
  numero_camisa       TEXT,
  altura_cm           INTEGER,
  data_nascimento     DATE,
  valor_mercado       NUMERIC(12,2),
  valor_mercado_moeda TEXT,                  -- ex: 'EUR'
  selecao_id          INTEGER REFERENCES dim_selecao(id),
  atualizado_em       TIMESTAMPTZ DEFAULT NOW()
);

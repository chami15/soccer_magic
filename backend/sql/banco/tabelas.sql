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

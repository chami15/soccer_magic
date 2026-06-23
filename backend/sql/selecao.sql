-- =====================================================
-- Soccer Magic — Banco v3 (modelo estrela)
-- DIM_SELECAO: atributos da seleção que mudam pouco/raramente.
-- =====================================================

--QUERY: create_table
CREATE TABLE IF NOT EXISTS dim_selecao (
  id            INTEGER PRIMARY KEY,   -- ID Sofascore do time
  nome          TEXT NOT NULL,
  continente    TEXT,
  grupo         TEXT,                  -- 'A' a 'L'
  ranking_fifa  INTEGER,                -- posição atual no ranking FIFA
  atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

--QUERY: enable_rls
ALTER TABLE dim_selecao ENABLE ROW LEVEL SECURITY;

--QUERY: create_policy_read
CREATE POLICY "public_read_dim_selecao" ON dim_selecao FOR SELECT USING (true);

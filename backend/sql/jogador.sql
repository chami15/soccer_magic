-- =====================================================
-- Soccer Magic — Banco v3 (modelo estrela)
-- DIM_JOGADOR: atributos do jogador, vistos nos incidentes
-- (gols/assistências) e no passing network do Sofascore.
-- =====================================================

--QUERY: create_table
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

--QUERY: enable_rls
ALTER TABLE dim_jogador ENABLE ROW LEVEL SECURITY;

--QUERY: create_policy_read
CREATE POLICY "public_read_dim_jogador" ON dim_jogador FOR SELECT USING (true);

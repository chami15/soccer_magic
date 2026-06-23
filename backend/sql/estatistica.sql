-- =====================================================
-- Soccer Magic — Banco v3 (modelo estrela)
-- FATO_ESTATISTICA_SELECAO_PARTIDA: 1 linha por seleção por
-- partida — estatísticas granulares (médias da janela passam
-- a ser VIEW/query sobre esta tabela, em vez de calculo no
-- pipeline Python).
-- =====================================================

--QUERY: create_table
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

--QUERY: enable_rls
ALTER TABLE fato_estatistica_selecao_partida ENABLE ROW LEVEL SECURITY;

--QUERY: create_policy_read
CREATE POLICY "public_read_fato_estatistica_selecao_partida" ON fato_estatistica_selecao_partida FOR SELECT USING (true);

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

--QUERY: upsert
INSERT INTO fato_estatistica_selecao_partida (
  partida_id, selecao_id, resultado, gols_marcados, gols_sofridos,
  posse_bola, chutes_total, chutes_no_gol, chutes_bloqueados,
  chutes_dentro_area, chutes_fora_area, escanteios, impedimentos,
  faltas, cartoes_amarelos, cartoes_vermelhos, defesas,
  passes_total, passes_certos, passes_precisao_pct,
  gols_1_tempo, gols_2_tempo, performance_rating
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (partida_id, selecao_id) DO UPDATE SET
  resultado = EXCLUDED.resultado,
  gols_marcados = EXCLUDED.gols_marcados,
  gols_sofridos = EXCLUDED.gols_sofridos,
  posse_bola = EXCLUDED.posse_bola,
  chutes_total = EXCLUDED.chutes_total,
  chutes_no_gol = EXCLUDED.chutes_no_gol,
  chutes_bloqueados = EXCLUDED.chutes_bloqueados,
  chutes_dentro_area = EXCLUDED.chutes_dentro_area,
  chutes_fora_area = EXCLUDED.chutes_fora_area,
  escanteios = EXCLUDED.escanteios,
  impedimentos = EXCLUDED.impedimentos,
  faltas = EXCLUDED.faltas,
  cartoes_amarelos = EXCLUDED.cartoes_amarelos,
  cartoes_vermelhos = EXCLUDED.cartoes_vermelhos,
  defesas = EXCLUDED.defesas,
  passes_total = EXCLUDED.passes_total,
  passes_certos = EXCLUDED.passes_certos,
  passes_precisao_pct = EXCLUDED.passes_precisao_pct,
  gols_1_tempo = EXCLUDED.gols_1_tempo,
  gols_2_tempo = EXCLUDED.gols_2_tempo,
  performance_rating = EXCLUDED.performance_rating
RETURNING *;

--QUERY: select_by_partida
SELECT * FROM fato_estatistica_selecao_partida WHERE partida_id = %s;

--QUERY: select_by_selecao
SELECT
  e.*,
  p.tipo,
  p.status,
  p.data_partida,
  p.selecao_home_id,
  p.selecao_away_id
FROM fato_estatistica_selecao_partida e
JOIN fato_partida p ON p.id = e.partida_id
WHERE e.selecao_id = %s AND p.status = 'finished'
ORDER BY p.data_partida DESC;

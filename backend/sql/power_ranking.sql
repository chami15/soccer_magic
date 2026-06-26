-- =====================================================
-- Soccer Magic — Banco v3 (modelo estrela)
-- FATO_POWER_RANKING_SELECAO: snapshot do Power Ranking do Sofascore
-- por rodada do torneio — substitui o ranking FIFA tradicional como
-- fonte de tendencia/momento, pois e atualizado a cada rodada (o
-- ranking FIFA em si ja vem direto em dim_selecao.ranking_fifa).
-- =====================================================

--QUERY: create_table
CREATE TABLE IF NOT EXISTS fato_power_ranking_selecao (
  selecao_id  INTEGER NOT NULL REFERENCES dim_selecao(id),
  round_id    INTEGER NOT NULL,   -- ID do round na API (ex: 133, 134...)
  round_num   INTEGER,            -- numero da rodada (1, 2, 3...)
  round_nome  TEXT,               -- ex: 'Pre-tournament', NULL se for so numero
  rank        INTEGER NOT NULL,
  pontos      INTEGER,
  rank_diff   INTEGER,
  criado_em   TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (selecao_id, round_id)
);

--QUERY: enable_rls
ALTER TABLE fato_power_ranking_selecao ENABLE ROW LEVEL SECURITY;

--QUERY: create_policy_read
CREATE POLICY "public_read_fato_power_ranking_selecao" ON fato_power_ranking_selecao FOR SELECT USING (true);

--QUERY: upsert
INSERT INTO fato_power_ranking_selecao (selecao_id, round_id, round_num, round_nome, rank, pontos, rank_diff)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (selecao_id, round_id) DO UPDATE SET
  round_num = EXCLUDED.round_num,
  round_nome = EXCLUDED.round_nome,
  rank = EXCLUDED.rank,
  pontos = EXCLUDED.pontos,
  rank_diff = EXCLUDED.rank_diff
RETURNING *;

--QUERY: select_by_selecao
SELECT * FROM fato_power_ranking_selecao WHERE selecao_id = %s ORDER BY round_id;

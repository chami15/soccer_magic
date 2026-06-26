-- =====================================================
-- Soccer Magic — Banco v3 (modelo estrela)
-- FATO_H2H_EVENTO: 1 linha por confronto direto historico entre
-- duas selecoes, vindo de /event/{customId}/h2h/events — escopo
-- mais amplo que fato_partida (cobre jogos de outros torneios
-- e anos anteriores, nao só a janela atual da Copa).
-- =====================================================

--QUERY: create_table
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

--QUERY: enable_rls
ALTER TABLE fato_h2h_evento ENABLE ROW LEVEL SECURITY;

--QUERY: create_policy_read
CREATE POLICY "public_read_fato_h2h_evento" ON fato_h2h_evento FOR SELECT USING (true);

--QUERY: upsert
INSERT INTO fato_h2h_evento (
  id, selecao_a_id, selecao_b_id, placar_a, placar_b, vencedor_id,
  torneio_nome, data_partida, performance_a, performance_b
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (id) DO UPDATE SET
  selecao_a_id = EXCLUDED.selecao_a_id,
  selecao_b_id = EXCLUDED.selecao_b_id,
  placar_a = EXCLUDED.placar_a,
  placar_b = EXCLUDED.placar_b,
  vencedor_id = EXCLUDED.vencedor_id,
  torneio_nome = EXCLUDED.torneio_nome,
  data_partida = EXCLUDED.data_partida,
  performance_a = EXCLUDED.performance_a,
  performance_b = EXCLUDED.performance_b
RETURNING *;

--QUERY: select_by_selecoes
SELECT * FROM fato_h2h_evento
WHERE (selecao_a_id = %s AND selecao_b_id = %s) OR (selecao_a_id = %s AND selecao_b_id = %s)
ORDER BY data_partida DESC;

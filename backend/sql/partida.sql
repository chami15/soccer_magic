-- =====================================================
-- Soccer Magic — Banco v3 (modelo estrela)
-- FATO_PARTIDA: 1 linha por jogo (passado ou futuro/agendado).
-- =====================================================

--QUERY: create_table
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

--QUERY: enable_rls
ALTER TABLE fato_partida ENABLE ROW LEVEL SECURITY;

--QUERY: create_policy_read
CREATE POLICY "public_read_fato_partida" ON fato_partida FOR SELECT USING (true);

--QUERY: upsert
INSERT INTO fato_partida (
  id, custom_id, selecao_home_id, selecao_away_id,
  placar_home, placar_away, placar_ht_home, placar_ht_away,
  status, vencedor_id, tipo, grupo, rodada, data_partida, cidade
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (id) DO UPDATE SET
  custom_id = EXCLUDED.custom_id,
  placar_home = EXCLUDED.placar_home,
  placar_away = EXCLUDED.placar_away,
  placar_ht_home = EXCLUDED.placar_ht_home,
  placar_ht_away = EXCLUDED.placar_ht_away,
  status = EXCLUDED.status,
  vencedor_id = EXCLUDED.vencedor_id,
  tipo = EXCLUDED.tipo,
  grupo = EXCLUDED.grupo,
  rodada = EXCLUDED.rodada,
  data_partida = EXCLUDED.data_partida,
  cidade = EXCLUDED.cidade,
  atualizado_em = NOW()
RETURNING *;

--QUERY: select_by_id
SELECT * FROM fato_partida WHERE id = %s;

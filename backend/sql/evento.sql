-- =====================================================
-- Soccer Magic — Banco v3 (modelo estrela)
-- FATO_EVENTO_PARTIDA: 1 linha por evento granular da partida
-- (gol, cartao, substituicao) — com jogador, assistencia e minuto.
-- jogador_id é reaproveitado: jogador que marcou (gol) ou que
-- recebeu o cartao (cartao_amarelo/vermelho). Em substituicao,
-- usar jogador_saida_id/jogador_entrada_id em vez de jogador_id.
-- Coordenadas de chute/passing network (footballPassingNetworkAction)
-- ficaram fora por granularidade/complexidade alta para o MVP —
-- avaliar no futuro como JSONB opcional se for necessario.
-- =====================================================

--QUERY: create_table
CREATE TABLE IF NOT EXISTS fato_evento_partida (
  id              INTEGER PRIMARY KEY,    -- ID Sofascore do incidente
  partida_id      INTEGER NOT NULL REFERENCES fato_partida(id),
  selecao_id      INTEGER NOT NULL REFERENCES dim_selecao(id),
  tipo_evento     TEXT NOT NULL,          -- 'gol' | 'cartao_amarelo' | 'cartao_vermelho' | 'substituicao'
  minuto          INTEGER NOT NULL,
  minuto_extra     INTEGER,                -- tempo de acrescimo, quando houver
  jogador_id      INTEGER REFERENCES dim_jogador(id),
  assistencia_jogador_id INTEGER REFERENCES dim_jogador(id),
  jogador_saida_id       INTEGER REFERENCES dim_jogador(id),  -- p/ substituicao
  jogador_entrada_id     INTEGER REFERENCES dim_jogador(id),  -- p/ substituicao
  tipo_gol        TEXT,                   -- 'regular' | 'penalty' | 'own-goal' | etc.
  var_decisao     TEXT,                   -- ex: 'goal_awarded' | 'goal_disallowed', quando houve revisao VAR
  criado_em       TIMESTAMPTZ DEFAULT NOW()
);

--QUERY: enable_rls
ALTER TABLE fato_evento_partida ENABLE ROW LEVEL SECURITY;

--QUERY: create_policy_read
CREATE POLICY "public_read_fato_evento_partida" ON fato_evento_partida FOR SELECT USING (true);

--QUERY: upsert
INSERT INTO fato_evento_partida (
  id, partida_id, selecao_id, tipo_evento, minuto, minuto_extra,
  jogador_id, assistencia_jogador_id, jogador_saida_id, jogador_entrada_id,
  tipo_gol, var_decisao
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (id) DO UPDATE SET
  partida_id = EXCLUDED.partida_id,
  selecao_id = EXCLUDED.selecao_id,
  tipo_evento = EXCLUDED.tipo_evento,
  minuto = EXCLUDED.minuto,
  minuto_extra = EXCLUDED.minuto_extra,
  jogador_id = EXCLUDED.jogador_id,
  assistencia_jogador_id = EXCLUDED.assistencia_jogador_id,
  jogador_saida_id = EXCLUDED.jogador_saida_id,
  jogador_entrada_id = EXCLUDED.jogador_entrada_id,
  tipo_gol = EXCLUDED.tipo_gol,
  var_decisao = EXCLUDED.var_decisao
RETURNING *;

--QUERY: select_by_partida
SELECT * FROM fato_evento_partida WHERE partida_id = %s ORDER BY minuto;


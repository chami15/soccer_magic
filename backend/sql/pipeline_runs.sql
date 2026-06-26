-- =====================================================
-- Soccer Magic — Banco v3 (modelo estrela)
-- PIPELINE_RUNS: log de execucoes do pipeline (igual ao schema antigo).
-- =====================================================

--QUERY: create_table
CREATE TABLE IF NOT EXISTS pipeline_runs (
  id               SERIAL PRIMARY KEY,
  started_at       TIMESTAMPTZ NOT NULL,
  finished_at      TIMESTAMPTZ,
  teams_processed  INTEGER DEFAULT 0,
  windows_changed  INTEGER DEFAULT 0,
  errors_count     INTEGER DEFAULT 0,
  error_log        JSONB,
  triggered_by     TEXT DEFAULT 'manual'
                     CHECK (triggered_by IN ('manual', 'cron'))
);

--QUERY: enable_rls
ALTER TABLE pipeline_runs ENABLE ROW LEVEL SECURITY;

--QUERY: create_policy_read
CREATE POLICY "public_read_pipeline_runs" ON pipeline_runs FOR SELECT USING (true);

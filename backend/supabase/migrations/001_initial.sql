-- =====================================================
-- Referência do schema SPECv2 (já aplicado via MCP apply_migration)
-- NÃO executar diretamente — usar o MCP do Supabase
-- =====================================================

CREATE TABLE IF NOT EXISTS teams (
  id           INTEGER PRIMARY KEY,  -- ID Sofascore do time
  name         TEXT NOT NULL,
  country      TEXT,
  flag_url     TEXT,                 -- URL da bandeira (Sofascore CDN)
  group_name   TEXT,                 -- 'A' a 'L'
  updated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS team_stats (
  team_id              INTEGER PRIMARY KEY REFERENCES teams(id),
  copa_count           INTEGER NOT NULL DEFAULT 0,
  friendly_count       INTEGER NOT NULL DEFAULT 0,
  data_quality         TEXT NOT NULL DEFAULT 'complete'
                         CHECK (data_quality IN ('complete', 'partial', 'insufficient')),
  games_window         JSONB,
  avg_goals_scored      NUMERIC(4,2),
  avg_goals_conceded    NUMERIC(4,2),
  avg_shots_total       NUMERIC(4,2),
  avg_shots_on_goal     NUMERIC(4,2),
  avg_shots_inside_box  NUMERIC(4,2),
  avg_shots_outside_box NUMERIC(4,2),
  avg_blocked_shots     NUMERIC(4,2),
  avg_corners           NUMERIC(4,2),
  avg_possession        NUMERIC(5,2),
  avg_passes_total      NUMERIC(6,2),
  avg_passes_accurate   NUMERIC(6,2),
  avg_passes_pct        NUMERIC(5,2),
  avg_offsides          NUMERIC(4,2),
  avg_fouls             NUMERIC(4,2),
  avg_yellow_cards      NUMERIC(4,2),
  avg_red_cards         NUMERIC(4,2),
  avg_saves             NUMERIC(4,2),
  clean_sheets          INTEGER,
  over15_pct            NUMERIC(5,2),
  over25_pct            NUMERIC(5,2),
  over35_pct            NUMERIC(5,2),
  btts_pct              NUMERIC(5,2),
  over35_corners_pct    NUMERIC(5,2),
  avg_goals_1h          NUMERIC(4,2),
  avg_goals_2h          NUMERIC(4,2),
  form_sequence         TEXT,
  trend_goals_3v5       NUMERIC(4,2),
  goal_distribution_summary JSONB,      -- resumo de /goal-distributions (agregado da temporada, escopo diferente da janela)
  tournament_overall_stats  JSONB,      -- /statistics/overall (agregado de TODOS os jogos da Copa, escopo diferente da janela)
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);

-- SPECv2: match_id (era fixture_id), tournament_id (era league_id), tournament_name (era league_name)
CREATE TABLE IF NOT EXISTS match_log (
  match_id        INTEGER PRIMARY KEY,    -- ID do evento no Sofascore
  team_id         INTEGER REFERENCES teams(id),
  opponent_name   TEXT,
  date            DATE,
  tournament_id   INTEGER,               -- ID do torneio no Sofascore
  tournament_name TEXT,
  match_type      TEXT CHECK (match_type IN ('Copa', 'Amistoso')),
  score_home      INTEGER,
  score_away      INTEGER,
  score_ht_home   INTEGER,
  score_ht_away   INTEGER,
  is_in_window    BOOLEAN DEFAULT FALSE,
  stats_raw       JSONB,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

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

-- Calendário do torneio: snapshot do /events/next/0 e /events/last/0 (uma chamada
-- cobre todas as 48 seleções de uma vez, vide collector.get_tournament_next_events).
CREATE TABLE IF NOT EXISTS matches_schedule (
  match_id        INTEGER PRIMARY KEY,    -- ID do evento no Sofascore
  custom_id       TEXT,                   -- usado em /event/{customId}/h2h/events
  home_team_id    INTEGER REFERENCES teams(id),
  away_team_id    INTEGER REFERENCES teams(id),
  home_team_name  TEXT,
  away_team_name  TEXT,
  group_name      TEXT,                   -- ex: 'Group I'
  round           INTEGER,
  match_date      DATE NOT NULL,          -- data do jogo (UTC), usada no filtro do frontend
  start_timestamp BIGINT NOT NULL,
  status_type     TEXT,                   -- 'notstarted' | 'finished' | 'inprogress'
  venue_city      TEXT,
  h2h_summary     JSONB,                  -- resumo de /event/{customId}/h2h/events (confrontos diretos passados)
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_match_log_team_id      ON match_log(team_id);
CREATE INDEX IF NOT EXISTS idx_match_log_is_in_window ON match_log(is_in_window) WHERE is_in_window = TRUE;
CREATE INDEX IF NOT EXISTS idx_teams_group_name        ON teams(group_name);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_started   ON pipeline_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_matches_schedule_date    ON matches_schedule(match_date);
CREATE INDEX IF NOT EXISTS idx_matches_schedule_group   ON matches_schedule(group_name);

ALTER TABLE teams             ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_stats        ENABLE ROW LEVEL SECURITY;
ALTER TABLE match_log         ENABLE ROW LEVEL SECURITY;
ALTER TABLE pipeline_runs     ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches_schedule  ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public_read_teams"            ON teams            FOR SELECT USING (true);
CREATE POLICY "public_read_team_stats"       ON team_stats       FOR SELECT USING (true);
CREATE POLICY "public_read_match_log"        ON match_log        FOR SELECT USING (true);
CREATE POLICY "public_read_pipeline_runs"    ON pipeline_runs    FOR SELECT USING (true);
CREATE POLICY "public_read_matches_schedule" ON matches_schedule FOR SELECT USING (true);
-- Escrita: apenas via service_role key (pipeline Python), que bypassa RLS

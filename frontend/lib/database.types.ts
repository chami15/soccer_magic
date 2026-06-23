export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      match_log: {
        Row: {
          created_at: string | null
          date: string | null
          is_in_window: boolean | null
          match_id: number
          match_type: string | null
          opponent_name: string | null
          score_away: number | null
          score_home: number | null
          score_ht_away: number | null
          score_ht_home: number | null
          stats_raw: Json | null
          team_id: number | null
          tournament_id: number | null
          tournament_name: string | null
        }
        Insert: {
          created_at?: string | null
          date?: string | null
          is_in_window?: boolean | null
          match_id: number
          match_type?: string | null
          opponent_name?: string | null
          score_away?: number | null
          score_home?: number | null
          score_ht_away?: number | null
          score_ht_home?: number | null
          stats_raw?: Json | null
          team_id?: number | null
          tournament_id?: number | null
          tournament_name?: string | null
        }
        Update: {
          created_at?: string | null
          date?: string | null
          is_in_window?: boolean | null
          match_id?: number
          match_type?: string | null
          opponent_name?: string | null
          score_away?: number | null
          score_home?: number | null
          score_ht_away?: number | null
          score_ht_home?: number | null
          stats_raw?: Json | null
          team_id?: number | null
          tournament_id?: number | null
          tournament_name?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "match_log_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      matches_schedule: {
        Row: {
          away_team_id: number | null
          away_team_name: string | null
          custom_id: string | null
          group_name: string | null
          h2h_summary: Json | null
          home_team_id: number | null
          home_team_name: string | null
          match_date: string
          match_id: number
          round: number | null
          start_timestamp: number
          status_type: string | null
          updated_at: string | null
          venue_city: string | null
        }
        Insert: {
          away_team_id?: number | null
          away_team_name?: string | null
          custom_id?: string | null
          group_name?: string | null
          h2h_summary?: Json | null
          home_team_id?: number | null
          home_team_name?: string | null
          match_date: string
          match_id: number
          round?: number | null
          start_timestamp: number
          status_type?: string | null
          updated_at?: string | null
          venue_city?: string | null
        }
        Update: {
          away_team_id?: number | null
          away_team_name?: string | null
          custom_id?: string | null
          group_name?: string | null
          h2h_summary?: Json | null
          home_team_id?: number | null
          home_team_name?: string | null
          match_date?: string
          match_id?: number
          round?: number | null
          start_timestamp?: number
          status_type?: string | null
          updated_at?: string | null
          venue_city?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "matches_schedule_home_team_id_fkey"
            columns: ["home_team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "matches_schedule_away_team_id_fkey"
            columns: ["away_team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      pipeline_runs: {
        Row: {
          error_log: Json | null
          errors_count: number | null
          finished_at: string | null
          id: number
          started_at: string
          teams_processed: number | null
          triggered_by: string | null
          windows_changed: number | null
        }
        Insert: {
          error_log?: Json | null
          errors_count?: number | null
          finished_at?: string | null
          id?: number
          started_at: string
          teams_processed?: number | null
          triggered_by?: string | null
          windows_changed?: number | null
        }
        Update: {
          error_log?: Json | null
          errors_count?: number | null
          finished_at?: string | null
          id?: number
          started_at?: string
          teams_processed?: number | null
          triggered_by?: string | null
          windows_changed?: number | null
        }
        Relationships: []
      }
      team_stats: {
        Row: {
          avg_blocked_shots: number | null
          avg_corners: number | null
          avg_fouls: number | null
          avg_goals_1h: number | null
          avg_goals_2h: number | null
          avg_goals_conceded: number | null
          avg_goals_scored: number | null
          avg_offsides: number | null
          avg_passes_accurate: number | null
          avg_passes_pct: number | null
          avg_passes_total: number | null
          avg_possession: number | null
          avg_red_cards: number | null
          avg_saves: number | null
          avg_shots_inside_box: number | null
          avg_shots_on_goal: number | null
          avg_shots_outside_box: number | null
          avg_shots_total: number | null
          avg_yellow_cards: number | null
          btts_pct: number | null
          clean_sheets: number | null
          copa_count: number
          data_quality: string
          form_sequence: string | null
          friendly_count: number
          games_window: Json | null
          goal_distribution_summary: Json | null
          over15_pct: number | null
          over25_pct: number | null
          over35_corners_pct: number | null
          over35_pct: number | null
          team_id: number
          tournament_overall_stats: Json | null
          trend_goals_3v5: number | null
          updated_at: string | null
        }
        Insert: {
          avg_blocked_shots?: number | null
          avg_corners?: number | null
          avg_fouls?: number | null
          avg_goals_1h?: number | null
          avg_goals_2h?: number | null
          avg_goals_conceded?: number | null
          avg_goals_scored?: number | null
          avg_offsides?: number | null
          avg_passes_accurate?: number | null
          avg_passes_pct?: number | null
          avg_passes_total?: number | null
          avg_possession?: number | null
          avg_red_cards?: number | null
          avg_saves?: number | null
          avg_shots_inside_box?: number | null
          avg_shots_on_goal?: number | null
          avg_shots_outside_box?: number | null
          avg_shots_total?: number | null
          avg_yellow_cards?: number | null
          btts_pct?: number | null
          clean_sheets?: number | null
          copa_count?: number
          data_quality?: string
          form_sequence?: string | null
          friendly_count?: number
          games_window?: Json | null
          goal_distribution_summary?: Json | null
          over15_pct?: number | null
          over25_pct?: number | null
          over35_corners_pct?: number | null
          over35_pct?: number | null
          team_id: number
          trend_goals_3v5?: number | null
          updated_at?: string | null
        }
        Update: {
          avg_blocked_shots?: number | null
          avg_corners?: number | null
          avg_fouls?: number | null
          avg_goals_1h?: number | null
          avg_goals_2h?: number | null
          avg_goals_conceded?: number | null
          avg_goals_scored?: number | null
          avg_offsides?: number | null
          avg_passes_accurate?: number | null
          avg_passes_pct?: number | null
          avg_passes_total?: number | null
          avg_possession?: number | null
          avg_red_cards?: number | null
          avg_saves?: number | null
          avg_shots_inside_box?: number | null
          avg_shots_on_goal?: number | null
          avg_shots_outside_box?: number | null
          avg_shots_total?: number | null
          avg_yellow_cards?: number | null
          btts_pct?: number | null
          clean_sheets?: number | null
          copa_count?: number
          data_quality?: string
          form_sequence?: string | null
          friendly_count?: number
          games_window?: Json | null
          goal_distribution_summary?: Json | null
          over15_pct?: number | null
          over25_pct?: number | null
          over35_corners_pct?: number | null
          over35_pct?: number | null
          team_id?: number
          tournament_overall_stats?: Json | null
          trend_goals_3v5?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "team_stats_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: true
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      teams: {
        Row: {
          country: string | null
          flag_url: string | null
          group_name: string | null
          id: number
          name: string
          updated_at: string | null
        }
        Insert: {
          country?: string | null
          flag_url?: string | null
          group_name?: string | null
          id: number
          name: string
          updated_at?: string | null
        }
        Update: {
          country?: string | null
          flag_url?: string | null
          group_name?: string | null
          id?: number
          name?: string
          updated_at?: string | null
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

export type Tables<T extends keyof Database['public']['Tables']> =
  Database['public']['Tables'][T]['Row']

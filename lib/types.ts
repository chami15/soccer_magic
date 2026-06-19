import type { Tables } from './database.types'

export type Team = Tables<'teams'>
export type TeamStats = Tables<'team_stats'>
export type MatchLog = Tables<'match_log'>
export type PipelineRun = Tables<'pipeline_runs'>

export type TeamWithStats = Team & { team_stats: TeamStats | null }

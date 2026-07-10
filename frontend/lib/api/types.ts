export type Nullable<T> = T | null

export interface SelectionStats {
  team_id: number
  data_quality: 'insufficient' | 'partial' | 'complete'
  copa_count: number
  friendly_count: number
  form_sequence: string | null
  goal_distribution_summary: unknown | null
  tournament_overall_stats: unknown | null
  avg_goals_scored: number | null
  avg_goals_conceded: number | null
  avg_corners: number | null
  avg_yellow_cards: number | null
  avg_red_cards: number | null
  avg_shots_on_goal: number | null
  avg_possession: number | null
  avg_goals_1h: number | null
  avg_goals_2h: number | null
  avg_shots_total: number | null
  avg_shots_inside_box: number | null
  avg_shots_outside_box: number | null
  avg_blocked_shots: number | null
  avg_passes_total: number | null
  avg_passes_accurate: number | null
  avg_offsides: number | null
  avg_fouls: number | null
  avg_saves: number | null
  over15_pct: number | null
  over25_pct: number | null
  over35_pct: number | null
  btts_pct: number | null
  clean_sheets: number | null
  over35_corners_pct: number | null
  avg_passes_pct: number | null
  trend_goals_3v5: number | null
}

export interface SelectionMatchSummary {
  partida_id: number
  tipo: string | null
  status: string | null
  data_partida: string | null
  selecao_home_id: number
  selecao_away_id: number
  resultado: 'V' | 'E' | 'D' | null
  gols_marcados: number | null
  gols_sofridos: number | null
  posse_bola: number | null
  chutes_total: number | null
  chutes_no_gol: number | null
  escanteios: number | null
  cartoes_amarelos: number | null
  cartoes_vermelhos: number | null
  performance_rating: number | null
}

export interface UpcomingMatch {
  id: number
  selecao_home_id: number
  selecao_home_nome: string | null
  selecao_away_id: number
  selecao_away_nome: string | null
  status: string | null
  tipo: string | null
  grupo: string | null
  rodada: number | null
  data_partida: string | null
  cidade: string | null
}

export interface PowerRankingRound {
  round_id: number
  round_num: number | null
  round_nome: string | null
  rank: number
  pontos: number | null
  rank_diff: number | null
}

export interface PowerRanking {
  selecao_id: number
  rank_atual: number
  pontos_atuais: number | null
  rank_diff_ultimo: number | null
  historico: PowerRankingRound[]
}

export interface HeadToHeadMatch {
  id: number
  selecao_a_id: number
  selecao_b_id: number
  placar_a: number | null
  placar_b: number | null
  vencedor_id: number | null
  torneio_nome: string | null
  data_partida: string | null
}

export interface HeadToHead {
  selecao_a_id: number
  selecao_b_id: number
  total_confrontos: number
  vitorias_a: number
  vitorias_b: number
  empates: number
  confrontos: HeadToHeadMatch[]
}

export interface PlayerItem {
  id: number
  nome: string
  nome_curto: string | null
  posicao: string | null
  numero_camisa: string | null
  valor_mercado: number | null
  moeda: string | null
}

export interface PlayersResponse {
  selecao_id: number
  total: number
  jogadores: PlayerItem[]
}

export interface TicketMarketPick {
  mercado: string
  pick: string
  probabilidade: number
  justificativa: string
}

export interface TicketSelectionPick {
  mercado: string
  pick: string
  confianca: number
}

export interface TicketCard {
  risco: 'baixo' | 'medio' | 'alto'
  tipo: 'simples' | 'multipla' | string
  selecoes: TicketSelectionPick[]
  justificativa: string
}

export interface TicketAnalysis {
  partida_id: number
  home: string
  away: string
  previsao_placar: string
  mercados_favoritos: TicketMarketPick[]
  analise: string
  bilhetes: TicketCard[]
}

export interface MatchContext {
  partida_id: number
  home_team_id: number
  home_team_name: string
  away_team_id: number
  away_team_name: string
  label: string
  source: 'upcoming' | 'history'
}

export interface MatchStatLine {
  partida_id: number
  selecao_id: number
  resultado: 'V' | 'E' | 'D' | null
  gols_marcados: number | null
  gols_sofridos: number | null
  posse_bola: number | null
  chutes_total: number | null
  chutes_no_gol: number | null
  chutes_bloqueados: number | null
  chutes_dentro_area: number | null
  chutes_fora_area: number | null
  escanteios: number | null
  impedimentos: number | null
  faltas: number | null
  cartoes_amarelos: number | null
  cartoes_vermelhos: number | null
  defesas: number | null
  passes_total: number | null
  passes_certos: number | null
  passes_precisao_pct: number | null
  gols_1_tempo: number | null
  gols_2_tempo: number | null
  performance_rating: number | null
}

export interface MatchEventLine {
  id: number
  partida_id: number
  selecao_id: number
  tipo_evento: 'gol' | 'cartao_amarelo' | 'cartao_vermelho' | 'substituicao' | string
  minuto: number
  minuto_extra: number | null
  jogador_id: number | null
  assistencia_jogador_id: number | null
  jogador_saida_id: number | null
  jogador_entrada_id: number | null
  tipo_gol: string | null
  var_decisao: string | null
}

export interface MatchDetail {
  id: number
  custom_id: string | null
  selecao_home_id: number
  selecao_away_id: number
  placar_home: number | null
  placar_away: number | null
  placar_ht_home: number | null
  placar_ht_away: number | null
  status: string | null
  vencedor_id: number | null
  tipo: string | null
  grupo: string | null
  rodada: number | null
  data_partida: string | null
  cidade: string | null
  estatisticas: MatchStatLine[]
  eventos: MatchEventLine[]
}

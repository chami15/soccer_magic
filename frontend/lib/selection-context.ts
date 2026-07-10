import type { MatchContext, SelectionMatchSummary, UpcomingMatch } from './api/types'

function formatMatchLabel(homeName: string, awayName: string, suffix?: string) {
  return suffix ? `${homeName} x ${awayName} • ${suffix}` : `${homeName} x ${awayName}`
}

export function resolveMatchContext(options: {
  selectionId: number
  selectionName: string
  upcomingMatches: UpcomingMatch[]
  historyMatches: SelectionMatchSummary[]
  teamNameById: Map<number, string>
}): MatchContext | null {
  const { selectionId, selectionName, upcomingMatches, historyMatches, teamNameById } = options

  const upcoming = upcomingMatches.find(
    (match) => match.selecao_home_id === selectionId || match.selecao_away_id === selectionId
  )

  if (upcoming) {
    return {
      partida_id: upcoming.id,
      home_team_id: upcoming.selecao_home_id,
      home_team_name: upcoming.selecao_home_nome ?? teamNameById.get(upcoming.selecao_home_id) ?? 'Home',
      away_team_id: upcoming.selecao_away_id,
      away_team_name: upcoming.selecao_away_nome ?? teamNameById.get(upcoming.selecao_away_id) ?? 'Away',
      label: formatMatchLabel(
        upcoming.selecao_home_nome ?? teamNameById.get(upcoming.selecao_home_id) ?? 'Home',
        upcoming.selecao_away_nome ?? teamNameById.get(upcoming.selecao_away_id) ?? 'Away',
        upcoming.cidade ?? upcoming.tipo ?? 'proxima partida'
      ),
      source: 'upcoming',
    }
  }

  const latestFinished = historyMatches[0]
  if (!latestFinished) return null

  const isHome = latestFinished.selecao_home_id === selectionId
  const homeId = latestFinished.selecao_home_id
  const awayId = latestFinished.selecao_away_id
  const homeName = teamNameById.get(homeId) ?? (isHome ? selectionName : 'Home')
  const awayName = teamNameById.get(awayId) ?? (!isHome ? selectionName : 'Away')

  return {
    partida_id: latestFinished.partida_id,
    home_team_id: homeId,
    home_team_name: homeName,
    away_team_id: awayId,
    away_team_name: awayName,
    label: formatMatchLabel(homeName, awayName, latestFinished.status ?? latestFinished.tipo ?? 'ultima partida'),
    source: 'history',
  }
}

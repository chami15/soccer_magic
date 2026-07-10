import { notFound } from 'next/navigation'
import { MatchDetailBoard } from '@/components/matches/MatchDetailBoard'
import { loadMatchDetails } from '@/lib/api/backend'
import { loadSelectionCatalog } from '@/lib/content/catalog'
import type { MatchContext } from '@/lib/api/types'

export const revalidate = 120

interface Props {
  params: { id: string }
}

export default async function MatchDetailPage({ params }: Props) {
  const matchId = Number(params.id)
  if (Number.isNaN(matchId)) notFound()

  const [teams, match] = await Promise.all([loadSelectionCatalog(), loadMatchDetails(matchId)])
  const homeTeam = teams.find((team) => team.id === match.selecao_home_id)
  const awayTeam = teams.find((team) => team.id === match.selecao_away_id)

  const matchContext: MatchContext = {
    partida_id: match.id,
    home_team_id: match.selecao_home_id,
    home_team_name: homeTeam?.name ?? `Seleção ${match.selecao_home_id}`,
    away_team_id: match.selecao_away_id,
    away_team_name: awayTeam?.name ?? `Seleção ${match.selecao_away_id}`,
    label: `${homeTeam?.name ?? `Seleção ${match.selecao_home_id}`} x ${awayTeam?.name ?? `Seleção ${match.selecao_away_id}`}`,
    source: match.status === 'finished' ? 'history' : 'upcoming',
  }

  return <MatchDetailBoard match={match} homeTeam={homeTeam} awayTeam={awayTeam} matchContext={matchContext} />
}

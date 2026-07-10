import { notFound } from 'next/navigation'
import { loadSelectionCatalog } from '@/lib/content/catalog'
import { loadPlayers, loadPowerRanking, loadSelectionMatches, loadSelectionStats, loadUpcomingMatches } from '@/lib/api/backend'
import { resolveMatchContext } from '@/lib/selection-context'
import type { SelectionStats } from '@/lib/api/types'
import { SelectionWorkspace } from '@/components/selection/SelectionWorkspace'

export const revalidate = 180

interface Props {
  params: { id: string }
}

export default async function TeamPage({ params }: Props) {
  const teamId = Number(params.id)
  if (Number.isNaN(teamId)) notFound()

  const teams = await loadSelectionCatalog()
  const team = teams.find((entry) => entry.id === teamId)
  if (!team) notFound()

  const teamNamesById = new Map(teams.map((entry) => [entry.id, entry.name]))
  const selectionStatsFallback = team.team_stats as SelectionStats | null

  const [statsResult, matchesResult, rankingResult, playersResult, upcomingResult] = await Promise.allSettled([
    loadSelectionStats(teamId),
    loadSelectionMatches(teamId),
    loadPowerRanking(teamId),
    loadPlayers(teamId),
    loadUpcomingMatches(20),
  ])

  const stats = statsResult.status === 'fulfilled' ? statsResult.value : selectionStatsFallback
  const matches = matchesResult.status === 'fulfilled' ? matchesResult.value.partidas : []
  const powerRanking = rankingResult.status === 'fulfilled' ? rankingResult.value : null
  const players = playersResult.status === 'fulfilled' ? playersResult.value.jogadores : []
  const upcomingMatches = upcomingResult.status === 'fulfilled' ? upcomingResult.value.partidas : []
  const matchContext = resolveMatchContext({
    selectionId: teamId,
    selectionName: team.name,
    upcomingMatches,
    historyMatches: matches,
    teamNameById: teamNamesById,
  })

  if (!stats) {
    return (
      <div className="glass-panel rounded-[2rem] p-8 text-center">
        <p className="section-title text-xs text-accent">Selecao</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-ink">{team.name}</h1>
        <p className="mt-3 text-sm text-muted">Estatisticas ainda nao disponiveis para esta selecao.</p>
      </div>
    )
  }

  return (
    <SelectionWorkspace
      team={team}
      stats={stats}
      matches={matches}
      teamNamesById={teamNamesById}
      powerRanking={powerRanking}
      players={players}
      matchContext={matchContext}
    />
  )
}

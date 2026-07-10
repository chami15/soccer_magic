import { loadUpcomingMatches } from '@/lib/api/backend'
import { MatchScheduleBoard } from '@/components/matches/MatchScheduleBoard'

export const revalidate = 120

export default async function MatchesPage() {
  const result = await Promise.allSettled([loadUpcomingMatches(50)])
  const partidas = result[0].status === 'fulfilled' ? result[0].value.partidas : []

  return <MatchScheduleBoard matches={partidas} />
}

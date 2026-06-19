import { notFound } from 'next/navigation'
import { createSupabaseServer } from '@/lib/supabase'
import { TeamStats } from '@/components/TeamStats'
import type { Database } from '@/lib/database.types'

type TeamRow    = Database['public']['Tables']['teams']['Row']
type StatsRow   = Database['public']['Tables']['team_stats']['Row']
type MatchRow   = Database['public']['Tables']['match_log']['Row']

export const revalidate = 300

interface Props {
  params: { id: string }
}

export default async function TeamPage({ params }: Props) {
  const teamId = Number(params.id)
  if (isNaN(teamId)) notFound()

  const supabase = createSupabaseServer()

  const { data: team, error: teamError } = await supabase
    .from('teams')
    .select<'*', TeamRow>('*')
    .eq('id', teamId)
    .single()

  if (teamError || !team) notFound()

  const [statsResult, matchesResult] = await Promise.all([
    supabase.from('team_stats').select<'*', StatsRow>('*').eq('team_id', teamId).single(),
    supabase
      .from('match_log')
      .select<'*', MatchRow>('*')
      .eq('team_id', teamId)
      .eq('is_in_window', true)
      .order('date', { ascending: false }),
  ])

  const stats = statsResult.data
  const matches = matchesResult.data ?? []

  if (!stats) {
    return (
      <div className="py-8 text-center text-text-secondary">
        <p className="text-4xl mb-4">⚽</p>
        <p>{team.name}</p>
        <p className="text-sm mt-2">Estatísticas ainda não disponíveis. Execute o pipeline.</p>
      </div>
    )
  }

  return <TeamStats team={team} stats={stats} matches={matches} />
}

import { createSupabaseServer } from '@/lib/supabase'
import { SimulateView } from '@/components/SimulateView'
import type { TeamWithStats } from '@/lib/types'

export const revalidate = 300

export default async function SimulatePage() {
  const supabase = createSupabaseServer()
  const { data: teams } = await supabase
    .from('teams')
    .select('*, team_stats(*)')
    .order('name', { ascending: true })

  const typedTeams = (teams ?? []) as unknown as TeamWithStats[]

  return <SimulateView teams={typedTeams} />
}

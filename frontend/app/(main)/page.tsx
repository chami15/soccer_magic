import { createSupabaseServer } from '@/lib/supabase'
import { TeamCard } from '@/components/TeamCard'
import { SearchTeams } from '@/components/SearchTeams'
import type { TeamWithStats } from '@/lib/types'

export const revalidate = 300

export default async function HomePage() {
  const supabase = createSupabaseServer()
  const { data: teams, error } = await supabase
    .from('teams')
    .select('*, team_stats(*)')
    .order('group_name', { ascending: true })
    .order('name', { ascending: true })

  if (error) {
    return (
      <div className="text-semantic-loss p-4">
        Erro ao carregar seleções: {error.message}
      </div>
    )
  }

  const typedTeams = (teams ?? []) as unknown as TeamWithStats[]

  return (
    <div className="flex flex-col gap-6 pb-8">
      {/* Header */}
      <div className="pt-2">
        <h1 className="text-3xl font-bold">
          <span className="text-neon">Soccer</span> Magic
        </h1>
        <p className="text-text-secondary text-sm mt-1">Copa do Mundo 2026 — 48 seleções</p>
      </div>

      {typedTeams.length === 0 ? (
        <div className="text-center py-16 text-text-secondary">
          <p className="text-4xl mb-4">⚽</p>
          <p className="font-medium">Nenhuma seleção carregada ainda.</p>
          <p className="text-sm mt-2">Execute o pipeline para importar os dados.</p>
        </div>
      ) : (
        <SearchTeams teams={typedTeams} />
      )}
    </div>
  )
}

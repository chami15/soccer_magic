import { createSupabaseServer } from '@/lib/supabase'
import { MatchScheduleFilters } from '@/components/MatchScheduleFilters'
import type { MatchSchedule } from '@/lib/types'

export const revalidate = 300

export default async function MatchesPage() {
  const supabase = createSupabaseServer()
  const { data: matches, error } = await supabase
    .from('matches_schedule')
    .select('*')
    .order('start_timestamp', { ascending: true })

  if (error) {
    return (
      <div className="text-semantic-loss p-4">
        Erro ao carregar calendário: {error.message}
      </div>
    )
  }

  const typedMatches = (matches ?? []) as unknown as MatchSchedule[]

  return (
    <div className="flex flex-col gap-6 pb-8">
      <div className="pt-2">
        <h1 className="text-3xl font-bold">
          <span className="text-neon">Calendário</span> da Copa
        </h1>
        <p className="text-text-secondary text-sm mt-1">Filtre por data ou grupo</p>
      </div>

      {typedMatches.length === 0 ? (
        <div className="text-center py-16 text-text-secondary">
          <p className="text-4xl mb-4">📅</p>
          <p className="font-medium">Nenhum jogo carregado ainda.</p>
          <p className="text-sm mt-2">Execute o pipeline para importar o calendário.</p>
        </div>
      ) : (
        <MatchScheduleFilters matches={typedMatches} />
      )}
    </div>
  )
}

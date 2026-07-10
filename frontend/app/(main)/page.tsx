import Link from 'next/link'
import { loadSelectionCatalog } from '@/lib/content/catalog'
import { loadUpcomingMatches } from '@/lib/api/backend'
import { SelectionDirectory } from '@/components/selection/SelectionDirectory'
import { UpcomingMatchesRail } from '@/components/matches/UpcomingMatchesRail'

export const revalidate = 180

export default async function HomePage() {
  const [teamsResult, matchesResult] = await Promise.allSettled([loadSelectionCatalog(), loadUpcomingMatches(8)])

  const teams = teamsResult.status === 'fulfilled' ? teamsResult.value : []
  const upcomingMatches = matchesResult.status === 'fulfilled' ? matchesResult.value.partidas : []
  const roundByTeamId = new Map<number, number | null>()

  for (const match of upcomingMatches) {
    const round = match.rodada ?? null
    if (round !== null) {
      const previousHome = roundByTeamId.get(match.selecao_home_id)
      const previousAway = roundByTeamId.get(match.selecao_away_id)
      if (previousHome === undefined || previousHome === null || round < previousHome) {
        roundByTeamId.set(match.selecao_home_id, round)
      }
      if (previousAway === undefined || previousAway === null || round < previousAway) {
        roundByTeamId.set(match.selecao_away_id, round)
      }
    }
  }

  return (
    <div className="space-y-8">
      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(20rem,0.75fr)]">
        <div className="glass-panel rounded-[2rem] p-6 sm:p-8">
          <div className="max-w-3xl space-y-5">
            <p className="section-title text-xs text-accent">Soccer intelligence</p>
            <h1 className="font-display text-4xl font-semibold leading-tight text-ink sm:text-5xl">
              Estatistica, contexto e bilhetes em uma interface limpa.
            </h1>
            <p className="max-w-2xl text-sm leading-relaxed text-muted sm:text-base">
              A plataforma organiza selecoes, partidas e leitura de aposta com visual institucional, ritmo suave e dados confiaveis.
            </p>

            <div className="flex flex-wrap gap-3">
              <Link
                href="/simulate"
                className="rounded-full bg-accent px-5 py-3 text-xs uppercase tracking-[0.22em] text-white shadow-soft transition-transform hover:-translate-y-0.5"
              >
                Abrir comparador
              </Link>
              <Link
                href="/matches"
                className="rounded-full border border-line/80 bg-paper/80 px-5 py-3 text-xs uppercase tracking-[0.22em] text-muted transition-colors hover:text-ink"
              >
                Ver calendario
              </Link>
            </div>

            <div className="grid gap-3 pt-2 sm:grid-cols-3">
              <div className="rounded-2xl border border-line/80 bg-canvas/55 p-4">
                <p className="text-xs uppercase tracking-[0.22em] text-muted">Selecoes</p>
                <p className="mt-2 font-display text-2xl font-semibold text-ink">{teams.length}</p>
              </div>
              <div className="rounded-2xl border border-line/80 bg-canvas/55 p-4">
                <p className="text-xs uppercase tracking-[0.22em] text-muted">Jogos proximos</p>
                <p className="mt-2 font-display text-2xl font-semibold text-ink">{upcomingMatches.length}</p>
              </div>
              <div className="rounded-2xl border border-line/80 bg-canvas/55 p-4">
                <p className="text-xs uppercase tracking-[0.22em] text-muted">Foco</p>
                <p className="mt-2 font-display text-2xl font-semibold text-ink">Copa 2026</p>
              </div>
            </div>
          </div>
        </div>

        <UpcomingMatchesRail matches={upcomingMatches} />
      </section>

      <SelectionDirectory teams={teams} roundByTeamId={roundByTeamId} />
    </div>
  )
}

import Link from 'next/link'
import type { SelectionMatchSummary } from '@/lib/api/types'

interface MatchHistoryProps {
  matches: SelectionMatchSummary[]
  teamId: number
  teamNamesById: Map<number, string>
}

function outcomeStyle(scored: number | null, conceded: number | null) {
  if (scored === null || conceded === null) return 'text-muted'
  if (scored > conceded) return 'text-risk-low'
  if (scored < conceded) return 'text-risk-high'
  return 'text-risk-medium'
}

function formatDate(value: string | null) {
  if (!value) return 'Sem data'
  return new Date(`${value}T00:00:00Z`).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    timeZone: 'UTC',
  })
}

export function MatchHistory({ matches, teamId, teamNamesById }: MatchHistoryProps) {
  if (!matches.length) {
    return <p className="text-sm text-muted">Nenhuma partida encontrada.</p>
  }

  return (
    <div className="grid gap-3">
      {matches.map((match) => {
        const isHome = match.selecao_home_id === teamId
        const opponentId = isHome ? match.selecao_away_id : match.selecao_home_id
        const opponentName = teamNamesById.get(opponentId) ?? `Selecao ${opponentId}`
        const homeScore = match.gols_marcados
        const awayScore = match.gols_sofridos
        const scoreText = homeScore === null || awayScore === null ? '—' : `${homeScore} - ${awayScore}`

        return (
          <Link
            key={match.partida_id}
            href={`/matches/${match.partida_id}`}
            className="block rounded-2xl border border-line/80 bg-paper/90 p-4 shadow-soft transition-transform duration-200 hover:-translate-y-0.5 hover:border-accent/30"
          >
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm font-medium text-ink">
                  {isHome ? 'Casa' : 'Fora'} vs {opponentName}
                </p>
                <p className="mt-1 text-xs uppercase tracking-[0.18em] text-muted">
                  {formatDate(match.data_partida)} • {match.tipo ?? 'Jogo'}
                </p>
              </div>

              <div className="flex items-center gap-3">
                <span
                  className={[
                    'rounded-full px-3 py-1 text-[11px] uppercase tracking-[0.18em]',
                    match.tipo === 'Copa'
                      ? 'border border-accent/20 bg-accent/10 text-accent'
                      : 'border border-line/80 bg-canvas/60 text-muted',
                  ].join(' ')}
                >
                  {match.tipo ?? 'Jogo'}
                </span>
                <span className={`font-mono text-lg font-semibold ${outcomeStyle(match.gols_marcados, match.gols_sofridos)}`}>
                  {scoreText}
                </span>
              </div>
            </div>
          </Link>
        )
      })}
    </div>
  )
}

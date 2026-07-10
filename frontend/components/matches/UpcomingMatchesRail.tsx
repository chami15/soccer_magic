import Link from 'next/link'
import type { UpcomingMatch } from '@/lib/api/types'

interface UpcomingMatchesRailProps {
  matches: UpcomingMatch[]
}

function formatDate(value: string | null) {
  if (!value) return 'Sem data'
  return new Date(`${value}T00:00:00Z`).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    weekday: 'short',
    timeZone: 'UTC',
  })
}

export function UpcomingMatchesRail({ matches }: UpcomingMatchesRailProps) {
  const preview = matches.slice(0, 5)

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between">
        <div>
          <p className="section-title text-xs text-accent">Calendario</p>
          <h2 className="font-display text-xl font-semibold text-ink">Proximos jogos</h2>
        </div>
        <Link href="/matches" className="text-sm text-accent transition-colors hover:text-accent-soft">
          Ver todos
        </Link>
      </div>

      <div className="grid gap-3">
        {preview.map((match) => (
          <Link
            key={match.id}
            href={`/matches/${match.id}`}
            className="rounded-2xl border border-line/80 bg-paper/85 p-4 shadow-soft transition-transform duration-200 hover:-translate-y-0.5 hover:border-accent/30"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-ink">
                  {match.selecao_home_nome ?? 'Casa'} x {match.selecao_away_nome ?? 'Fora'}
                </p>
                <p className="mt-1 text-xs uppercase tracking-[0.18em] text-muted">
                  {match.grupo ?? 'Sem grupo'} • {formatDate(match.data_partida)}
                </p>
              </div>
              <span
                className={[
                  'rounded-full px-3 py-1 text-[11px] uppercase tracking-[0.18em]',
                  match.status === 'finished'
                    ? 'border border-line/80 bg-canvas/60 text-muted'
                    : 'border border-accent/20 bg-accent/10 text-accent',
                ].join(' ')}
              >
                {match.status === 'finished' ? 'Encerrado' : 'Agendado'}
              </span>
            </div>
          </Link>
        ))}

        {preview.length === 0 && (
          <div className="rounded-2xl border border-line/80 bg-paper/85 p-6 text-sm text-muted">
            Nenhum jogo encontrado.
          </div>
        )}
      </div>
    </div>
  )
}

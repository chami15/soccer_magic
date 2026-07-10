import Image from 'next/image'
import Link from 'next/link'
import { FormBadge } from '@/components/ui/FormBadge'
import { WindowBadge } from '@/components/ui/WindowBadge'
import type { TeamWithStats } from '@/lib/types'

interface SelectionCardProps {
  team: TeamWithStats
}

export function SelectionCard({ team }: SelectionCardProps) {
  const stats = team.team_stats
  const form = stats?.form_sequence?.split(' ').filter(Boolean) ?? []

  return (
    <Link
      href={`/teams/${team.id}`}
      className="group block rounded-2xl border border-line/80 bg-paper/90 p-4 shadow-soft transition-transform duration-200 hover:-translate-y-1 hover:border-accent/30"
    >
      <div className="flex items-start gap-4">
        <div className="flex h-14 w-14 flex-none items-center justify-center overflow-hidden rounded-2xl border border-line/70 bg-canvas/60">
          {team.flag_url ? (
            <Image src={team.flag_url} alt={team.name} width={56} height={42} className="h-full w-full object-cover" unoptimized />
          ) : (
            <span className="font-display text-sm tracking-[0.3em] text-muted">FC</span>
          )}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h3 className="truncate font-display text-base font-semibold text-ink">{team.name}</h3>
              <p className="text-xs uppercase tracking-[0.2em] text-muted">Grupo {team.group_name ?? 'Sem grupo'}</p>
            </div>
            {stats?.avg_goals_scored !== null && stats?.avg_goals_scored !== undefined && (
              <div className="rounded-full border border-accent/20 bg-accent/8 px-3 py-1 text-right">
                <p className="font-mono text-sm text-accent">{stats.avg_goals_scored.toFixed(2)}</p>
                <p className="text-[10px] uppercase tracking-[0.18em] text-muted">gols/jogo</p>
              </div>
            )}
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-2">
            <div className="flex gap-1">
              {form.slice(0, 5).map((result, index) => (
                <FormBadge key={`${team.id}-${index}`} result={result as 'V' | 'E' | 'D'} />
              ))}
            </div>
            {stats && (
              <WindowBadge
                copaCount={stats.copa_count}
                friendlyCount={stats.friendly_count}
                dataQuality={stats.data_quality}
              />
            )}
          </div>
        </div>
      </div>
    </Link>
  )
}

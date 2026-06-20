import Link from 'next/link'
import Image from 'next/image'
import { FormBadge } from './ui/FormBadge'
import { WindowBadge } from './ui/WindowBadge'
import type { TeamWithStats } from '@/lib/types'

interface TeamCardProps {
  team: TeamWithStats
}

export function TeamCard({ team }: TeamCardProps) {
  const stats = team.team_stats
  const form = stats?.form_sequence?.split(' ').filter(Boolean) ?? []

  return (
    <Link href={`/teams/${team.id}`}>
      <div
        className="flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all hover:border-neon-dark/50"
        style={{
          background: '#1A1A24',
          border: '1px solid #334155',
        }}
      >
        {team.flag_url && (
          <Image
            src={team.flag_url}
            alt={team.name}
            width={40}
            height={30}
            className="rounded object-cover flex-shrink-0"
            unoptimized
          />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <span className="text-text-primary font-medium truncate">{team.name}</span>
            {stats && (
              <span className="font-mono text-neon text-sm flex-shrink-0">
                {stats.avg_goals_scored !== null ? stats.avg_goals_scored?.toFixed(2) : '—'}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            <div className="flex gap-1">
              {form.slice(0, 5).map((r, i) => (
                <FormBadge key={i} result={r as 'V' | 'E' | 'D'} />
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

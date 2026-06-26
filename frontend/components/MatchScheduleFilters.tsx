'use client'

import { useMemo, useState } from 'react'
import type { MatchSchedule } from '@/lib/types'

interface MatchScheduleFiltersProps {
  matches: MatchSchedule[]
}

function formatDateLabel(isoDate: string): string {
  return new Date(`${isoDate}T00:00:00Z`).toLocaleDateString('pt-BR', {
    weekday: 'short',
    day: '2-digit',
    month: '2-digit',
    timeZone: 'UTC',
  })
}

export function MatchScheduleFilters({ matches }: MatchScheduleFiltersProps) {
  const dates = useMemo(
    () => Array.from(new Set(matches.map((m) => m.match_date))).sort(),
    [matches]
  )
  const groups = useMemo(
    () =>
      Array.from(new Set(matches.map((m) => m.group_name).filter((g): g is string => !!g))).sort(),
    [matches]
  )

  const [selectedDate, setSelectedDate] = useState('')
  const [selectedGroup, setSelectedGroup] = useState('')

  const filtered = matches.filter(
    (m) =>
      (!selectedDate || m.match_date === selectedDate) &&
      (!selectedGroup || m.group_name === selectedGroup)
  )

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap gap-3">
        <select
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="bg-bg-elevated border border-neon-dark/40 rounded-lg px-4 py-2.5 text-text-primary text-sm focus:outline-none focus:border-neon"
        >
          <option value="">Todas as datas</option>
          {dates.map((d) => (
            <option key={d} value={d}>
              {formatDateLabel(d)}
            </option>
          ))}
        </select>

        <select
          value={selectedGroup}
          onChange={(e) => setSelectedGroup(e.target.value)}
          className="bg-bg-elevated border border-neon-dark/40 rounded-lg px-4 py-2.5 text-text-primary text-sm focus:outline-none focus:border-neon"
        >
          <option value="">Todos os grupos</option>
          {groups.map((g) => (
            <option key={g} value={g}>
              {g}
            </option>
          ))}
        </select>
      </div>

      {filtered.length === 0 ? (
        <p className="text-text-secondary text-sm text-center py-8">
          Nenhum jogo encontrado para esse filtro.
        </p>
      ) : (
        <div className="flex flex-col gap-2">
          {filtered.map((m) => (
            <div
              key={m.match_id}
              className="flex items-center justify-between bg-bg-elevated border border-text-border/30 rounded-lg px-4 py-3"
            >
              <div>
                <p className="text-sm font-medium text-text-primary">
                  {m.home_team_name} x {m.away_team_name}
                </p>
                <p className="text-xs text-text-secondary mt-0.5">
                  {m.group_name ?? 'Sem grupo'} · {formatDateLabel(m.match_date)}
                  {m.venue_city ? ` · ${m.venue_city}` : ''}
                </p>
              </div>
              <span
                className={`text-xs px-2 py-1 rounded ${
                  m.status_type === 'finished'
                    ? 'bg-text-border/30 text-text-secondary'
                    : 'text-neon bg-neon-dark/10'
                }`}
              >
                {m.status_type === 'finished' ? 'Encerrado' : 'Agendado'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

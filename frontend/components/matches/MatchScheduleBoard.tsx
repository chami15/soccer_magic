'use client'

import Link from 'next/link'
import { useMemo, useState } from 'react'
import type { UpcomingMatch } from '@/lib/api/types'

interface MatchScheduleBoardProps {
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

export function MatchScheduleBoard({ matches }: MatchScheduleBoardProps) {
  const [selectedDate, setSelectedDate] = useState('')
  const [selectedGroup, setSelectedGroup] = useState('')

  const dates = useMemo(
    () => Array.from(new Set(matches.map((match) => match.data_partida).filter((date): date is string => Boolean(date)))).sort(),
    [matches]
  )
  const groups = useMemo(
    () => Array.from(new Set(matches.map((match) => match.grupo).filter((group): group is string => Boolean(group)))).sort(),
    [matches]
  )

  const filtered = useMemo(
    () =>
      matches.filter((match) => {
        const matchesDate = !selectedDate || match.data_partida === selectedDate
        const matchesGroup = !selectedGroup || match.grupo === selectedGroup
        return matchesDate && matchesGroup
      }),
    [matches, selectedDate, selectedGroup]
  )

  return (
    <section className="space-y-6">
      <div className="glass-panel rounded-3xl p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="section-title text-xs text-accent">Calendario</p>
            <h1 className="font-display text-2xl font-semibold text-ink">Agenda da Copa</h1>
            <p className="mt-2 max-w-2xl text-sm text-muted">Filtre os proximos jogos por data e grupo.</p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <select
              value={selectedDate}
              onChange={(event) => setSelectedDate(event.target.value)}
              className="rounded-2xl border border-line/80 bg-canvas/60 px-4 py-3 text-sm text-ink outline-none"
            >
              <option value="">Todas as datas</option>
              {dates.map((date) => (
                <option key={date} value={date}>
                  {formatDate(date)}
                </option>
              ))}
            </select>

            <select
              value={selectedGroup}
              onChange={(event) => setSelectedGroup(event.target.value)}
              className="rounded-2xl border border-line/80 bg-canvas/60 px-4 py-3 text-sm text-ink outline-none"
            >
              <option value="">Todos os grupos</option>
              {groups.map((group) => (
                <option key={group} value={group}>
                  Grupo {group}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid gap-4">
        {filtered.map((match) => (
        <Link key={match.id} href={`/matches/${match.id}`} className="block rounded-2xl border border-line/80 bg-paper/90 p-4 shadow-soft transition-transform duration-200 hover:-translate-y-0.5 hover:border-accent/30">
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="font-display text-base font-semibold text-ink">
                  {match.selecao_home_nome ?? 'Casa'} x {match.selecao_away_nome ?? 'Fora'}
                </p>
                <p className="mt-1 text-xs uppercase tracking-[0.18em] text-muted">
                  {match.grupo ?? 'Sem grupo'} • Rodada {match.rodada ?? '-'} • {formatDate(match.data_partida)}
                </p>
                {match.cidade && <p className="mt-1 text-sm text-muted">{match.cidade}</p>}
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

        {filtered.length === 0 && (
          <div className="rounded-2xl border border-line/80 bg-paper/90 p-8 text-sm text-muted">
            Nenhum jogo encontrado para esse filtro.
          </div>
        )}
      </div>
    </section>
  )
}

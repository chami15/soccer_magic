'use client'

import { useMemo, useState } from 'react'
import { SelectionCard } from './SelectionCard'
import type { TeamWithStats } from '@/lib/types'

interface SelectionDirectoryProps {
  teams: TeamWithStats[]
  roundByTeamId?: Map<number, number | null>
}

type SortMode = 'group' | 'round' | 'name-asc' | 'name-desc' | 'ranking'

function rankingValue(team: TeamWithStats) {
  return team.team_stats?.avg_goals_scored ?? -1
}

export function SelectionDirectory({ teams, roundByTeamId }: SelectionDirectoryProps) {
  const [search, setSearch] = useState('')
  const [sortMode, setSortMode] = useState<SortMode>('group')

  const filteredTeams = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase()
    const base = normalizedSearch
      ? teams.filter((team) => team.name.toLowerCase().includes(normalizedSearch))
      : teams

    const sorted = [...base]
    switch (sortMode) {
      case 'round':
        return sorted.sort((left, right) => {
          const leftRound = roundByTeamId?.get(left.id) ?? Number.MAX_SAFE_INTEGER
          const rightRound = roundByTeamId?.get(right.id) ?? Number.MAX_SAFE_INTEGER
          const byRound = leftRound - rightRound
          return byRound !== 0 ? byRound : left.name.localeCompare(right.name, 'pt-BR')
        })
      case 'name-asc':
        return sorted.sort((left, right) => left.name.localeCompare(right.name, 'pt-BR'))
      case 'name-desc':
        return sorted.sort((left, right) => right.name.localeCompare(left.name, 'pt-BR'))
      case 'ranking':
        return sorted.sort((left, right) => rankingValue(right) - rankingValue(left))
      case 'group':
      default:
        return sorted.sort((left, right) => {
          const leftGroup = left.group_name ?? 'ZZ'
          const rightGroup = right.group_name ?? 'ZZ'
          const byGroup = leftGroup.localeCompare(rightGroup, 'pt-BR')
          return byGroup !== 0 ? byGroup : left.name.localeCompare(right.name, 'pt-BR')
        })
    }
  }, [search, sortMode, teams])

  const groupedTeams = useMemo(() => {
    if (sortMode !== 'group') return null

    return filteredTeams.reduce<Record<string, TeamWithStats[]>>((accumulator, team) => {
      const group = team.group_name ?? 'Sem grupo'
      if (!accumulator[group]) accumulator[group] = []
      accumulator[group].push(team)
      return accumulator
    }, {})
  }, [filteredTeams, sortMode])

  const sections = groupedTeams ? Object.keys(groupedTeams).sort() : []

  return (
    <section className="space-y-6">
      <div className="glass-panel rounded-3xl p-4 sm:p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="space-y-2">
            <p className="section-title text-xs text-accent">Selecoes</p>
            <h2 className="font-display text-2xl font-semibold text-ink">Escolha, compare e aprofunde</h2>
            <p className="max-w-2xl text-sm text-muted">
              Navegue pelas selecoes, filtre por nome ou grupo e abra a ficha analitica com estatisticas e bilhetes.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_minmax(0,12rem)]">
            <label className="flex min-w-0 items-center rounded-2xl border border-line/80 bg-canvas/60 px-4 py-3">
              <input
                type="text"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Buscar selecao..."
                className="w-full bg-transparent text-sm text-ink outline-none placeholder:text-muted"
              />
            </label>

            <select
              value={sortMode}
              onChange={(event) => setSortMode(event.target.value as SortMode)}
              className="rounded-2xl border border-line/80 bg-canvas/60 px-4 py-3 text-sm text-ink outline-none"
            >
              <option value="group">Agrupar por grupo</option>
              <option value="round">Rodada</option>
              <option value="name-asc">Nome A-Z</option>
              <option value="name-desc">Nome Z-A</option>
              <option value="ranking">Forca ofensiva</option>
            </select>
          </div>
        </div>
      </div>

      {filteredTeams.length === 0 ? (
        <div className="glass-panel rounded-3xl p-10 text-center text-sm text-muted">Nenhuma selecao encontrada.</div>
      ) : sortMode === 'group' && groupedTeams ? (
        <div className="space-y-8">
          {sections.map((group) => (
            <section key={group} className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="section-title text-xs text-muted">Grupo {group}</h3>
                <span className="rounded-full border border-line/80 bg-paper/70 px-3 py-1 text-[11px] uppercase tracking-[0.18em] text-muted">
                  {groupedTeams[group].length} selecoes
                </span>
              </div>
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {groupedTeams[group].map((team) => (
                  <SelectionCard key={team.id} team={team} />
                ))}
              </div>
            </section>
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filteredTeams.map((team) => (
            <SelectionCard key={team.id} team={team} />
          ))}
        </div>
      )}
    </section>
  )
}

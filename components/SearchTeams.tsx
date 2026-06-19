'use client'

import { useState } from 'react'
import { TeamCard } from './TeamCard'
import type { TeamWithStats } from '@/lib/types'

interface SearchTeamsProps {
  teams: TeamWithStats[]
}

export function SearchTeams({ teams }: SearchTeamsProps) {
  const [search, setSearch] = useState('')

  const filtered = search
    ? teams.filter((t) => t.name.toLowerCase().includes(search.toLowerCase()))
    : teams

  const groups = filtered.reduce<Record<string, TeamWithStats[]>>((acc, team) => {
    const g = team.group_name ?? 'Sem grupo'
    if (!acc[g]) acc[g] = []
    acc[g].push(team)
    return acc
  }, {})

  const groupKeys = Object.keys(groups).sort()

  return (
    <div className="flex flex-col gap-6">
      {/* SearchBar */}
      <input
        type="text"
        placeholder="Buscar seleção..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full bg-bg-elevated border border-neon-dark/40 rounded-lg px-4 py-2.5 text-text-primary placeholder-text-secondary focus:outline-none focus:border-neon text-sm"
      />

      {filtered.length === 0 ? (
        <p className="text-text-secondary text-sm text-center py-8">
          Nenhuma seleção encontrada para &quot;{search}&quot;
        </p>
      ) : (
        groupKeys.map((group) => (
          <div key={group}>
            <h2 className="text-text-secondary text-xs uppercase tracking-widest mb-3">
              Grupo {group}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {groups[group].map((team) => (
                <TeamCard key={team.id} team={team} />
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  )
}

'use client'

import { useState } from 'react'
import Image from 'next/image'
import { FormBadge } from './ui/FormBadge'
import { DoubleBar } from './ui/DoubleBar'
import { createSupabaseBrowser } from '@/lib/supabase'
import type { TeamWithStats } from '@/lib/types'

interface SimulateViewProps {
  teams: TeamWithStats[]
}

const categories = [
  {
    label: 'Ofensivo',
    metrics: [
      { key: 'avg_goals_scored', label: 'Gols/jogo' },
      { key: 'avg_shots_on_goal', label: 'Chutes ao gol' },
      { key: 'avg_shots_total', label: 'Chutes totais' },
      { key: 'avg_shots_inside_box', label: 'Chutes dentro área' },
    ],
  },
  {
    label: 'Defensivo',
    metrics: [
      { key: 'avg_goals_conceded', label: 'Gols sofridos' },
      { key: 'avg_saves', label: 'Defesas goleiro' },
      { key: 'clean_sheets', label: 'Clean sheets' },
    ],
  },
  {
    label: 'Territorial',
    metrics: [
      { key: 'avg_possession', label: 'Posse %' },
      { key: 'avg_corners', label: 'Escanteios' },
      { key: 'avg_passes_pct', label: 'Precisão passes %' },
    ],
  },
  {
    label: 'Disciplinar',
    metrics: [
      { key: 'avg_fouls', label: 'Faltas' },
      { key: 'avg_yellow_cards', label: 'Cartões amarelos' },
      { key: 'avg_red_cards', label: 'Cartões vermelhos' },
    ],
  },
  {
    label: 'Apostas',
    metrics: [
      { key: 'over15_pct', label: 'Over 1.5 %' },
      { key: 'over25_pct', label: 'Over 2.5 %' },
      { key: 'btts_pct', label: 'BTTS %' },
      { key: 'over35_corners_pct', label: 'Over 3.5 cant. %' },
    ],
  },
]

export function SimulateView({ teams }: SimulateViewProps) {
  const [teamAId, setTeamAId] = useState<string>('')
  const [teamBId, setTeamBId] = useState<string>('')

  const teamA = teams.find((t) => String(t.id) === teamAId)
  const teamB = teams.find((t) => String(t.id) === teamBId)

  const statsA = teamA?.team_stats
  const statsB = teamB?.team_stats

  function countLeading(): number {
    if (!statsA || !statsB) return 0
    let count = 0
    for (const cat of categories) {
      for (const { key } of cat.metrics) {
        const a = (statsA as any)[key] ?? 0
        const b = (statsB as any)[key] ?? 0
        if (a > b) count++
      }
    }
    return count
  }

  const totalMetrics = categories.reduce((sum, c) => sum + c.metrics.length, 0)
  const aLeads = countLeading()

  return (
    <div className="flex flex-col gap-6 pb-24">
      <h1 className="text-text-primary text-2xl font-bold">
        Simule seu <span className="text-neon">jogo</span>
      </h1>

      {/* Seletores */}
      <div className="flex items-center gap-3">
        <select
          value={teamAId}
          onChange={(e) => setTeamAId(e.target.value)}
          className="flex-1 bg-bg-elevated border border-neon-dark/40 text-text-primary rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-neon"
        >
          <option value="">Seleção A</option>
          {teams.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </select>
        <span className="text-text-secondary font-bold">vs</span>
        <select
          value={teamBId}
          onChange={(e) => setTeamBId(e.target.value)}
          className="flex-1 bg-bg-elevated border border-neon-dark/40 text-text-primary rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-neon"
        >
          <option value="">Seleção B</option>
          {teams.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
        </select>
      </div>

      {teamA && teamB && statsA && statsB && (
        <>
          {/* Header dos times */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {teamA.flag_url && (
                <Image src={teamA.flag_url} alt={teamA.name} width={32} height={24} unoptimized className="rounded" />
              )}
              <span className="text-text-primary font-semibold text-sm">{teamA.name}</span>
            </div>
            <span className="text-text-secondary text-xs">vs</span>
            <div className="flex items-center gap-2">
              <span className="text-text-primary font-semibold text-sm">{teamB.name}</span>
              {teamB.flag_url && (
                <Image src={teamB.flag_url} alt={teamB.name} width={32} height={24} unoptimized className="rounded" />
              )}
            </div>
          </div>

          {/* Forma side by side */}
          <div className="flex justify-between">
            <div className="flex gap-1">
              {statsA.form_sequence?.split(' ').filter(Boolean).map((r, i) => (
                <FormBadge key={i} result={r as 'V' | 'E' | 'D'} />
              ))}
            </div>
            <div className="flex gap-1">
              {statsB.form_sequence?.split(' ').filter(Boolean).map((r, i) => (
                <FormBadge key={i} result={r as 'V' | 'E' | 'D'} />
              ))}
            </div>
          </div>

          {/* Categorias */}
          {categories.map((cat) => (
            <div key={cat.label}>
              <h2 className="text-text-secondary text-xs uppercase tracking-widest mb-2">{cat.label}</h2>
              <div
                className="rounded-lg p-4 flex flex-col"
                style={{ background: '#1A1A24', border: '1px solid #334155' }}
              >
                {cat.metrics.map(({ key, label }) => (
                  <DoubleBar
                    key={key}
                    label={label}
                    valueA={(statsA as any)[key]}
                    valueB={(statsB as any)[key]}
                  />
                ))}
              </div>
            </div>
          ))}

          {/* Resumo */}
          <div
            className="rounded-lg p-4 text-center"
            style={{ background: '#1A1A24', border: '1px solid rgba(168,85,247,0.3)' }}
          >
            <p className="text-text-primary">
              <span className="text-neon font-bold">{teamA.name}</span> lidera em{' '}
              <span className="font-mono text-neon">{aLeads}</span> de{' '}
              <span className="font-mono">{totalMetrics}</span> categorias
            </p>
          </div>
        </>
      )}

      {!teamA && !teamB && (
        <div className="text-text-secondary text-sm text-center py-8">
          Selecione duas seleções para comparar
        </div>
      )}
    </div>
  )
}

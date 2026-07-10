'use client'

import { useEffect, useMemo, useState } from 'react'
import Image from 'next/image'
import { FormBadge } from '@/components/ui/FormBadge'
import { DoubleBar } from '@/components/ui/DoubleBar'
import type { HeadToHead } from '@/lib/api/types'
import type { TeamWithStats } from '@/lib/types'

interface CompareBoardProps {
  teams: TeamWithStats[]
}

const metrics = [
  {
    label: 'Ofensivo',
    items: [
      { key: 'avg_goals_scored', label: 'Gols/jogo', better: 'high' as const },
      { key: 'avg_shots_on_goal', label: 'Chutes ao gol', better: 'high' as const },
      { key: 'avg_shots_total', label: 'Chutes totais', better: 'high' as const },
      { key: 'avg_shots_inside_box', label: 'Chutes dentro da area', better: 'high' as const },
    ],
  },
  {
    label: 'Defensivo',
    items: [
      { key: 'avg_goals_conceded', label: 'Gols sofridos', better: 'low' as const },
      { key: 'avg_saves', label: 'Defesas', better: 'high' as const },
      { key: 'clean_sheets', label: 'Clean sheets', better: 'high' as const },
    ],
  },
  {
    label: 'Territorial',
    items: [
      { key: 'avg_possession', label: 'Posse %', better: 'high' as const },
      { key: 'avg_corners', label: 'Escanteios', better: 'high' as const },
      { key: 'avg_passes_pct', label: 'Precisao de passes %', better: 'high' as const },
    ],
  },
  {
    label: 'Disciplina',
    items: [
      { key: 'avg_fouls', label: 'Faltas', better: 'low' as const },
      { key: 'avg_yellow_cards', label: 'Amarelos', better: 'low' as const },
      { key: 'avg_red_cards', label: 'Vermelhos', better: 'low' as const },
    ],
  },
]

function numericStat(stats: TeamWithStats['team_stats'], key: string) {
  if (!stats) return null
  const raw = (stats as Record<string, unknown>)[key]
  return typeof raw === 'number' ? raw : null
}

export function CompareBoard({ teams }: CompareBoardProps) {
  const [teamAId, setTeamAId] = useState('')
  const [teamBId, setTeamBId] = useState('')
  const [h2h, setH2h] = useState<HeadToHead | null>(null)
  const [loadingH2H, setLoadingH2H] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const teamA = teams.find((team) => String(team.id) === teamAId) ?? null
  const teamB = teams.find((team) => String(team.id) === teamBId) ?? null

  useEffect(() => {
    if (!teamA || !teamB) {
      setH2h(null)
      setError(null)
      return
    }

    let cancelled = false
    setLoadingH2H(true)
    setError(null)

    fetch(`/api/h2h/${teamA.id}/${teamB.id}`)
      .then(async (response) => {
        const payload = await response.json()
        if (!response.ok) throw new Error(payload.error || 'Falha ao carregar H2H')
        return payload as HeadToHead
      })
      .then((payload) => {
        if (!cancelled) setH2h(payload)
      })
      .catch((requestError) => {
        if (!cancelled) setError(requestError instanceof Error ? requestError.message : 'Falha ao carregar H2H')
      })
      .finally(() => {
        if (!cancelled) setLoadingH2H(false)
      })

    return () => {
      cancelled = true
    }
  }, [teamA, teamB])

  const totalLeading = useMemo(() => {
    if (!teamA?.team_stats || !teamB?.team_stats) return 0

    let count = 0
    for (const group of metrics) {
      for (const item of group.items) {
        const valueA = numericStat(teamA.team_stats, item.key) ?? 0
        const valueB = numericStat(teamB.team_stats, item.key) ?? 0
        const aBetter = item.better === 'low' ? valueA < valueB : valueA > valueB
        if (aBetter) count += 1
      }
    }

    return count
  }, [teamA, teamB])

  return (
    <section className="space-y-6">
      <div className="glass-panel rounded-[2rem] p-5 sm:p-6">
        <div className="space-y-5">
          <div>
            <p className="section-title text-xs text-accent">Comparador</p>
            <h1 className="mt-2 font-display text-3xl font-semibold text-ink">Analise lado a lado</h1>
            <p className="mt-2 max-w-2xl text-sm text-muted">
              Escolha duas selecoes e compare forca ofensiva, equilibrio defensivo e leitura de aposta.
            </p>
          </div>

          <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)]">
            <select
              value={teamAId}
              onChange={(event) => setTeamAId(event.target.value)}
              className="rounded-2xl border border-line/80 bg-canvas/60 px-4 py-3 text-sm text-ink outline-none"
            >
              <option value="">Selecao A</option>
              {teams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.name}
                </option>
              ))}
            </select>

            <div className="flex items-center justify-center text-xs uppercase tracking-[0.22em] text-muted">
              vs
            </div>

            <select
              value={teamBId}
              onChange={(event) => setTeamBId(event.target.value)}
              className="rounded-2xl border border-line/80 bg-canvas/60 px-4 py-3 text-sm text-ink outline-none"
            >
              <option value="">Selecao B</option>
              {teams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {teamA && teamB && teamA.team_stats && teamB.team_stats ? (
        <div className="space-y-6">
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)]">
            <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
              <div className="flex items-center gap-3">
                {teamA.flag_url && <Image src={teamA.flag_url} alt={teamA.name} width={42} height={32} unoptimized className="rounded-lg" />}
                <div>
                  <p className="font-display text-xl font-semibold text-ink">{teamA.name}</p>
                  <p className="text-xs uppercase tracking-[0.2em] text-muted">Grupo {teamA.group_name ?? '-'}</p>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {(teamA.team_stats.form_sequence?.split(' ').filter(Boolean) ?? []).map((result: string, index: number) => (
                  <FormBadge key={`${teamA.id}-form-${index}`} result={result as 'V' | 'E' | 'D'} />
                ))}
              </div>
            </div>

            <div className="flex items-center justify-center rounded-[1.75rem] border border-line/80 bg-paper/70 px-4 py-5 text-center shadow-soft">
              <div>
                <p className="text-xs uppercase tracking-[0.22em] text-muted">Vantagem</p>
                <p className="mt-2 font-display text-3xl font-semibold text-accent">{totalLeading}</p>
                <p className="mt-1 text-xs uppercase tracking-[0.18em] text-muted">métricas lideradas</p>
              </div>
            </div>

            <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
              <div className="flex items-center gap-3 justify-end text-right">
                <div>
                  <p className="font-display text-xl font-semibold text-ink">{teamB.name}</p>
                  <p className="text-xs uppercase tracking-[0.2em] text-muted">Grupo {teamB.group_name ?? '-'}</p>
                </div>
                {teamB.flag_url && <Image src={teamB.flag_url} alt={teamB.name} width={42} height={32} unoptimized className="rounded-lg" />}
              </div>
              <div className="mt-4 flex flex-wrap justify-end gap-2">
                {(teamB.team_stats.form_sequence?.split(' ').filter(Boolean) ?? []).map((result: string, index: number) => (
                  <FormBadge key={`${teamB.id}-form-${index}`} result={result as 'V' | 'E' | 'D'} />
                ))}
              </div>
            </div>
          </div>

          {metrics.map((group) => (
            <section key={group.label} className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
              <div className="flex items-end justify-between">
                <h2 className="section-title text-xs text-muted">{group.label}</h2>
                <span className="text-xs uppercase tracking-[0.18em] text-muted">{group.items.length} metricas</span>
              </div>
              <div className="mt-3 space-y-1">
                {group.items.map((metric) => (
                  <DoubleBar
                    key={metric.key}
                    label={metric.label}
                    valueA={numericStat(teamA.team_stats, metric.key)}
                    valueB={numericStat(teamB.team_stats, metric.key)}
                    reverse={metric.better === 'low'}
                  />
                ))}
              </div>
            </section>
          ))}

          <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_minmax(0,0.9fr)]">
            <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
              <p className="section-title text-xs text-muted">H2H</p>
              {loadingH2H ? (
                <p className="mt-3 text-sm text-muted">Carregando confronto direto...</p>
              ) : error ? (
                <p className="mt-3 text-sm text-risk-high">{error}</p>
              ) : h2h ? (
                <div className="mt-4 space-y-4">
                  <div className="grid gap-3 sm:grid-cols-4">
                    <div className="rounded-2xl border border-line/80 bg-canvas/50 p-4 text-center">
                      <p className="text-xs uppercase tracking-[0.18em] text-muted">Total</p>
                      <p className="mt-2 font-display text-2xl font-semibold text-ink">{h2h.total_confrontos}</p>
                    </div>
                    <div className="rounded-2xl border border-line/80 bg-canvas/50 p-4 text-center">
                      <p className="text-xs uppercase tracking-[0.18em] text-muted">{teamA.name}</p>
                      <p className="mt-2 font-display text-2xl font-semibold text-risk-low">{h2h.vitorias_a}</p>
                    </div>
                    <div className="rounded-2xl border border-line/80 bg-canvas/50 p-4 text-center">
                      <p className="text-xs uppercase tracking-[0.18em] text-muted">Empates</p>
                      <p className="mt-2 font-display text-2xl font-semibold text-risk-medium">{h2h.empates}</p>
                    </div>
                    <div className="rounded-2xl border border-line/80 bg-canvas/50 p-4 text-center">
                      <p className="text-xs uppercase tracking-[0.18em] text-muted">{teamB.name}</p>
                      <p className="mt-2 font-display text-2xl font-semibold text-risk-high">{h2h.vitorias_b}</p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    {h2h.confrontos.slice(0, 5).map((match) => (
                      <div key={match.id} className="flex items-center justify-between rounded-2xl border border-line/70 bg-canvas/50 px-4 py-3">
                        <div>
                          <p className="text-sm font-medium text-ink">{match.torneio_nome ?? 'Confronto'}</p>
                          <p className="text-xs uppercase tracking-[0.18em] text-muted">{match.data_partida ?? 'Sem data'}</p>
                        </div>
                        <p className="font-mono text-sm text-ink">
                          {match.placar_a ?? '-'} - {match.placar_b ?? '-'}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="mt-3 text-sm text-muted">Selecione as duas selecoes para abrir o confronto direto.</p>
              )}
            </div>

            <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
              <p className="section-title text-xs text-muted">Resumo tecnico</p>
              <div className="mt-4 space-y-3">
                <div className="rounded-2xl border border-line/70 bg-canvas/50 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-muted">Window score</p>
                  <p className="mt-2 text-sm text-ink">
                    {teamA.name} e {teamB.name} comparam janela recente, forma e tendencia em uma leitura objetiva.
                  </p>
                </div>
                <div className="rounded-2xl border border-line/70 bg-canvas/50 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-muted">Uso ideal</p>
                  <p className="mt-2 text-sm text-ink">
                    Esta tela serve para decidir qual selecao tem melhor perfil estatistico e contexto de aposta.
                  </p>
                </div>
              </div>
            </div>
          </section>
        </div>
      ) : (
        <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-10 text-center text-sm text-muted shadow-soft">
          Selecione duas selecoes para iniciar a comparacao.
        </div>
      )}
    </section>
  )
}

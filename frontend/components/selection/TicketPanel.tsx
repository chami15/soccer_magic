'use client'

import { useMemo, useState } from 'react'
import type { MatchContext, TicketAnalysis } from '@/lib/api/types'

interface TicketPanelProps {
  matchContext: MatchContext | null
}

const riskStyles: Record<string, string> = {
  baixo: 'border-risk-low/25 bg-risk-low/10 text-risk-low',
  medio: 'border-risk-medium/25 bg-risk-medium/10 text-risk-medium',
  alto: 'border-risk-high/25 bg-risk-high/10 text-risk-high',
}

function riskLabel(risk: string) {
  if (risk === 'baixo') return 'Baixo risco'
  if (risk === 'medio') return 'Médio risco'
  return 'Alto risco'
}

function moneylineLabel(type: string) {
  if (type === 'simples') return 'Simples'
  if (type === 'multipla') return 'Múltipla'
  return type
}

export function TicketPanel({ matchContext }: TicketPanelProps) {
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState<TicketAnalysis | null>(null)
  const [error, setError] = useState<string | null>(null)

  const canGenerate = Boolean(matchContext)

  const favoriteMarkets = useMemo(() => analysis?.mercados_favoritos ?? [], [analysis])

  async function generateTicket() {
    if (!matchContext) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/analise/${matchContext.partida_id}`)
      const payload = (await response.json()) as TicketAnalysis & { error?: string }

      if (!response.ok) {
        throw new Error(payload.error || 'Falha ao gerar bilhetes')
      }

      setAnalysis(payload)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Falha ao gerar bilhetes')
    } finally {
      setLoading(false)
    }
  }

  return (
    <aside className="glass-panel sticky top-[6.5rem] rounded-3xl p-5">
      <div className="space-y-4">
        <div className="space-y-2">
          <p className="section-title text-xs text-accent">Bilhetes</p>
          <h2 className="font-display text-2xl font-semibold text-ink">Analise de aposta</h2>
          {matchContext ? (
            <p className="text-sm text-muted">
              Base: {matchContext.label}
            </p>
          ) : (
            <p className="text-sm text-muted">
              Selecione uma partida para gerar a leitura do agente.
            </p>
          )}
        </div>

        {!analysis ? (
          <div className="rounded-3xl border border-dashed border-line/90 bg-canvas/50 px-6 py-12 text-center">
            <button
              type="button"
              onClick={generateTicket}
              disabled={!canGenerate || loading}
              className="mx-auto inline-flex min-w-[14rem] items-center justify-center rounded-full bg-accent px-6 py-3 font-display text-sm font-semibold uppercase tracking-[0.24em] text-white shadow-soft transition-transform duration-200 hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? 'Gerando...' : 'Gerar bilhete'}
            </button>
            <p className="mt-4 text-xs uppercase tracking-[0.22em] text-muted">
              Bilhetes com risco baixo, medio e alto
            </p>
          </div>
        ) : (
          <div className="space-y-5">
            <div className="rounded-3xl border border-accent/20 bg-accent/8 p-4">
              <p className="section-title text-[10px] text-accent-soft">Previsao</p>
              <div className="mt-2 flex items-end justify-between gap-4">
                <div>
                  <h3 className="font-display text-3xl font-semibold text-ink">{analysis.previsao_placar}</h3>
                  <p className="mt-1 text-sm text-muted">
                    {analysis.home} x {analysis.away}
                  </p>
                </div>
                <div className="rounded-full border border-line/80 bg-paper/80 px-3 py-1 text-xs uppercase tracking-[0.2em] text-muted">
                  {analysis.mercados_favoritos.length} mercados
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h3 className="section-title text-xs text-muted">Mercados favoritos</h3>
              <div className="space-y-3">
                {favoriteMarkets.map((market) => (
                  <article key={`${market.mercado}-${market.pick}`} className="rounded-2xl border border-line/80 bg-paper/90 p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-medium text-ink">{market.mercado}</p>
                        <p className="mt-1 text-sm text-muted">{market.pick}</p>
                      </div>
                      <div className="rounded-full border border-accent/20 bg-accent/8 px-3 py-1 text-sm font-mono text-accent">
                        {market.probabilidade.toFixed(2)}%
                      </div>
                    </div>
                    <p className="mt-3 text-sm leading-relaxed text-muted">{market.justificativa}</p>
                  </article>
                ))}
              </div>
            </div>

            <div className="rounded-3xl border border-line/80 bg-paper/90 p-4">
              <h3 className="section-title text-xs text-muted">Leitura do agente</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink">{analysis.analise}</p>
            </div>

            <div className="space-y-3">
              <h3 className="section-title text-xs text-muted">Bilhetes sugeridos</h3>
              <div className="space-y-3">
                {analysis.bilhetes.map((ticket) => (
                  <article key={`${ticket.risco}-${ticket.tipo}-${ticket.selecoes.length}`} className={`rounded-2xl border p-4 ${riskStyles[ticket.risco] ?? 'border-line/80 bg-paper/90 text-ink'}`}>
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div>
                        <p className="font-display text-base font-semibold text-ink">{riskLabel(ticket.risco)}</p>
                        <p className="text-xs uppercase tracking-[0.2em] text-muted">{moneylineLabel(ticket.tipo)}</p>
                      </div>
                      <span className="rounded-full border border-current/15 px-3 py-1 text-xs uppercase tracking-[0.18em]">
                        {ticket.selecoes.length} selecao{ticket.selecoes.length > 1 ? 'es' : ''}
                      </span>
                    </div>

                    <div className="mt-4 space-y-2">
                      {ticket.selecoes.map((selection) => (
                        <div key={`${ticket.risco}-${selection.mercado}-${selection.pick}`} className="rounded-xl border border-white/10 bg-canvas/35 px-4 py-3">
                          <div className="flex items-start justify-between gap-4">
                            <div>
                              <p className="text-sm font-medium text-ink">{selection.mercado}</p>
                              <p className="mt-1 text-sm text-muted">{selection.pick}</p>
                            </div>
                            <div className="rounded-full border border-current/15 px-3 py-1 text-sm font-mono text-ink">
                              {selection.confianca}%
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    <p className="mt-3 text-sm leading-relaxed text-ink/90">{ticket.justificativa}</p>
                  </article>
                ))}
              </div>
            </div>
          </div>
        )}

        {error && <div className="rounded-2xl border border-risk-high/25 bg-risk-high/10 p-4 text-sm text-risk-high">{error}</div>}
      </div>
    </aside>
  )
}

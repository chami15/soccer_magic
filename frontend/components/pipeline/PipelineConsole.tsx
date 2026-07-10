'use client'

import { useState } from 'react'
import type { PipelineRun } from '@/lib/types'

interface PipelineConsoleProps {
  runs: PipelineRun[]
}

function formatDate(value: string | null) {
  if (!value) return '—'
  return new Date(value).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function PipelineConsole({ runs }: PipelineConsoleProps) {
  const [loading, setLoading] = useState(false)
  const [log, setLog] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const latest = runs[0]

  async function triggerPipeline() {
    setLoading(true)
    setLog(null)
    setError(null)

    try {
      const response = await fetch('/api/pipeline', { method: 'POST' })
      const payload = await response.json()

      if (!response.ok || !payload.success) {
        throw new Error(payload.error || 'Falha ao executar pipeline')
      }

      setLog(payload.log || 'Pipeline executado com sucesso.')
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Falha ao executar pipeline')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="space-y-6">
      <div className="glass-panel rounded-[2rem] p-6">
        <p className="section-title text-xs text-accent">Pipeline</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-ink">Operacao tecnica</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted">
          Area restrita para acompanhar execucoes, logs e o ultimo estado do carregamento de dados.
        </p>
      </div>

      {latest && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
            <p className="section-title text-xs text-muted">Ultima execucao</p>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl border border-line/70 bg-canvas/50 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-muted">Inicio</p>
                <p className="mt-2 font-mono text-sm text-ink">{formatDate(latest.started_at)}</p>
              </div>
              <div className="rounded-2xl border border-line/70 bg-canvas/50 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-muted">Fim</p>
                <p className="mt-2 font-mono text-sm text-ink">{formatDate(latest.finished_at)}</p>
              </div>
              <div className="rounded-2xl border border-line/70 bg-canvas/50 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-muted">Selecoes</p>
                <p className="mt-2 font-mono text-sm text-accent">{latest.teams_processed ?? 0}</p>
              </div>
              <div className="rounded-2xl border border-line/70 bg-canvas/50 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-muted">Janelas</p>
                <p className="mt-2 font-mono text-sm text-ink">{latest.windows_changed ?? 0}</p>
              </div>
            </div>
          </div>

          <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
            <p className="section-title text-xs text-muted">Status</p>
            <div className="mt-4 space-y-3">
              <div className="rounded-2xl border border-line/70 bg-canvas/50 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-muted">Erros</p>
                <p className={`mt-2 font-mono text-sm ${(latest.errors_count ?? 0) > 0 ? 'text-risk-high' : 'text-risk-low'}`}>
                  {latest.errors_count ?? 0}
                </p>
              </div>
              <button
                type="button"
                onClick={triggerPipeline}
                disabled={loading}
                className="inline-flex w-full items-center justify-center rounded-full bg-accent px-5 py-3 text-xs uppercase tracking-[0.22em] text-white transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? 'Executando...' : 'Atualizar dados'}
              </button>
            </div>
          </div>
        </div>
      )}

      {log && <pre className="rounded-[1.75rem] border border-risk-low/20 bg-risk-low/10 p-5 text-xs leading-relaxed text-risk-low whitespace-pre-wrap">{log}</pre>}
      {error && <pre className="rounded-[1.75rem] border border-risk-high/20 bg-risk-high/10 p-5 text-xs leading-relaxed text-risk-high whitespace-pre-wrap">{error}</pre>}

      <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
        <div className="flex items-end justify-between">
          <h2 className="section-title text-xs text-muted">Historico recente</h2>
          <span className="text-xs uppercase tracking-[0.18em] text-muted">{runs.length} execucoes</span>
        </div>

        <div className="mt-4 grid gap-3">
          {runs.slice(0, 5).map((run) => (
            <div key={run.id} className="flex flex-col gap-2 rounded-2xl border border-line/70 bg-canvas/50 p-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-mono text-xs text-muted">{formatDate(run.started_at)}</p>
                <p className="mt-1 text-sm text-ink">Executado por {run.triggered_by ?? 'manual'}</p>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <span className="font-mono text-accent">{run.teams_processed ?? 0} times</span>
                <span className={`font-mono ${(run.errors_count ?? 0) > 0 ? 'text-risk-high' : 'text-risk-low'}`}>
                  {(run.errors_count ?? 0) === 0 ? 'ok' : `${run.errors_count} erros`}
                </span>
              </div>
            </div>
          ))}
          {runs.length === 0 && <p className="text-sm text-muted">Nenhuma execucao registrada.</p>}
        </div>
      </div>
    </section>
  )
}

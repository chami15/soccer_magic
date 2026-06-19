'use client'

import { useState } from 'react'
import type { PipelineRun } from '@/lib/types'

interface PipelineStatusProps {
  runs: PipelineRun[]
}

function formatDate(ts: string | null) {
  if (!ts) return '—'
  return new Date(ts).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function PipelineStatus({ runs }: PipelineStatusProps) {
  const [loading, setLoading] = useState(false)
  const [log, setLog] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const latest = runs[0]

  async function triggerPipeline() {
    setLoading(true)
    setLog(null)
    setError(null)
    try {
      const res = await fetch('/api/pipeline', { method: 'POST' })
      const data = await res.json()
      if (data.success) {
        setLog(data.log || 'Pipeline concluído.')
      } else {
        setError(data.error || 'Erro desconhecido.')
      }
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-6 pb-24">
      <h1 className="text-text-primary text-2xl font-bold">Pipeline de dados</h1>

      {/* Status card */}
      {latest && (
        <div
          className="rounded-lg p-4 flex flex-col gap-3"
          style={{ background: '#1A1A24', border: '1px solid rgba(168,85,247,0.25)' }}
        >
          <h2 className="text-text-secondary text-xs uppercase tracking-widest">Última execução</h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-xs text-text-secondary">Iniciado</p>
              <p className="font-mono text-sm text-text-primary">{formatDate(latest.started_at)}</p>
            </div>
            <div>
              <p className="text-xs text-text-secondary">Finalizado</p>
              <p className="font-mono text-sm text-text-primary">{formatDate(latest.finished_at)}</p>
            </div>
            <div>
              <p className="text-xs text-text-secondary">Seleções</p>
              <p className="font-mono text-sm text-neon">{latest.teams_processed ?? 0}</p>
            </div>
            <div>
              <p className="text-xs text-text-secondary">Janelas alteradas</p>
              <p className="font-mono text-sm text-text-primary">{latest.windows_changed ?? 0}</p>
            </div>
            <div>
              <p className="text-xs text-text-secondary">Erros</p>
              <p className={`font-mono text-sm ${(latest.errors_count ?? 0) > 0 ? 'text-semantic-loss' : 'text-semantic-win'}`}>
                {latest.errors_count ?? 0}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Botão trigger */}
      <button
        onClick={triggerPipeline}
        disabled={loading}
        className="w-full py-3 rounded-lg font-semibold text-white transition-all disabled:opacity-50"
        style={{
          background: loading ? '#334155' : 'linear-gradient(to right, #7C3AED, #A855F7)',
          boxShadow: loading ? 'none' : '0 0 16px #A855F740',
        }}
      >
        {loading ? '⏳ Atualizando...' : '⚡ Atualizar dados'}
      </button>

      {log && (
        <pre className="text-xs text-semantic-win bg-bg-elevated rounded-lg p-4 overflow-auto whitespace-pre-wrap">
          {log}
        </pre>
      )}
      {error && (
        <pre className="text-xs text-semantic-loss bg-bg-elevated rounded-lg p-4 overflow-auto whitespace-pre-wrap">
          {error}
        </pre>
      )}

      {/* Histórico de execuções */}
      <div>
        <h2 className="text-text-secondary text-xs uppercase tracking-widest mb-3">
          Histórico de execuções
        </h2>
        <div className="flex flex-col gap-2">
          {runs.slice(0, 5).map((run) => (
            <div
              key={run.id}
              className="flex items-center justify-between p-3 rounded-lg text-sm"
              style={{ background: '#1A1A24', border: '1px solid #334155' }}
            >
              <span className="text-text-secondary font-mono text-xs">{formatDate(run.started_at)}</span>
              <div className="flex gap-3">
                <span className="text-neon font-mono">{run.teams_processed ?? 0} times</span>
                <span className={`font-mono ${(run.errors_count ?? 0) > 0 ? 'text-semantic-loss' : 'text-semantic-win'}`}>
                  {(run.errors_count ?? 0) === 0 ? '✓ ok' : `${run.errors_count} erros`}
                </span>
              </div>
            </div>
          ))}
          {runs.length === 0 && (
            <p className="text-text-secondary text-sm">Nenhuma execução registrada.</p>
          )}
        </div>
      </div>
    </div>
  )
}

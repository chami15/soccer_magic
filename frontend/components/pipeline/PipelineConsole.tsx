'use client'

import { useState } from 'react'

export function PipelineConsole() {
  const [loading, setLoading] = useState(false)
  const [log, setLog] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [ranAt, setRanAt] = useState<Date | null>(null)

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
      setRanAt(new Date())
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Falha ao executar pipeline')
      setRanAt(new Date())
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
          Dispara o pipeline de coleta de dados do Sofascore: partidas, estatisticas, rankings e H2H.
          O processo leva entre 2 e 10 minutos dependendo do volume.
        </p>
      </div>

      <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-6 shadow-soft">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-display text-base font-semibold text-ink">Atualizar dados</p>
            <p className="mt-1 text-sm text-muted">
              {ranAt
                ? `Ultima execucao: ${ranAt.toLocaleString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`
                : 'Nenhuma execucao nesta sessao.'}
            </p>
          </div>
          <button
            type="button"
            onClick={triggerPipeline}
            disabled={loading}
            className="inline-flex min-w-[14rem] items-center justify-center rounded-full bg-accent px-6 py-3 text-xs uppercase tracking-[0.22em] text-white shadow-soft transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? 'Executando...' : 'Executar pipeline'}
          </button>
        </div>

        {loading && (
          <div className="mt-5 rounded-2xl border border-accent/20 bg-accent/8 px-5 py-4 text-sm text-accent">
            Pipeline em execucao — aguarde, isso pode levar alguns minutos...
          </div>
        )}
      </div>

      {log && (
        <div className="space-y-2">
          <p className="section-title text-xs text-muted">Log de saida</p>
          <pre className="overflow-x-auto rounded-[1.75rem] border border-risk-low/20 bg-risk-low/10 p-5 text-xs leading-relaxed text-risk-low whitespace-pre-wrap">
            {log}
          </pre>
        </div>
      )}

      {error && (
        <div className="space-y-2">
          <p className="section-title text-xs text-muted">Erro</p>
          <pre className="overflow-x-auto rounded-[1.75rem] border border-risk-high/20 bg-risk-high/10 p-5 text-xs leading-relaxed text-risk-high whitespace-pre-wrap">
            {error}
          </pre>
        </div>
      )}

      <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
        <h2 className="section-title text-xs text-muted">O que o pipeline faz</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {[
            ['Calendario', 'Importa todas as partidas da Copa 2026 com datas e grupos'],
            ['Estatisticas', 'Coleta os ultimos 5 jogos de cada selecao (Copa + amistosos)'],
            ['Rankings', 'Atualiza o power ranking com o round mais recente'],
            ['H2H', 'Busca o historico de confrontos diretos para cada partida'],
          ].map(([title, desc]) => (
            <div key={title} className="rounded-2xl border border-line/70 bg-canvas/50 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-accent">{title}</p>
              <p className="mt-2 text-sm text-muted">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

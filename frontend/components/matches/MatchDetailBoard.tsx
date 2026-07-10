import Image from 'next/image'
import type { MatchContext, MatchDetail, MatchStatLine } from '@/lib/api/types'
import type { TeamWithStats } from '@/lib/types'
import { DoubleBar } from '@/components/ui/DoubleBar'
import { KpiCard } from '@/components/ui/KpiCard'
import { TicketPanel } from '@/components/selection/TicketPanel'

interface MatchDetailBoardProps {
  match: MatchDetail
  homeTeam?: TeamWithStats
  awayTeam?: TeamWithStats
  matchContext: MatchContext
}

function formatDate(value: string | null) {
  if (!value) return 'Sem data'
  const date = value.includes('T') ? new Date(value) : new Date(`${value}T00:00:00Z`)
  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
  })
}

function getStat(match: MatchDetail, teamId: number): MatchStatLine | null {
  return match.estatisticas.find((entry) => entry.selecao_id === teamId) ?? null
}

function eventLabel(type: string) {
  if (type === 'gol') return 'Gol'
  if (type === 'cartao_amarelo') return 'Cartão amarelo'
  if (type === 'cartao_vermelho') return 'Cartão vermelho'
  if (type === 'substituicao') return 'Substituição'
  return type
}

function eventStyle(type: string) {
  if (type === 'gol') return 'border-risk-low/20 bg-risk-low/10 text-risk-low'
  if (type === 'cartao_amarelo') return 'border-risk-medium/20 bg-risk-medium/10 text-risk-medium'
  if (type === 'cartao_vermelho') return 'border-risk-high/20 bg-risk-high/10 text-risk-high'
  return 'border-line/80 bg-canvas/60 text-muted'
}

export function MatchDetailBoard({ match, homeTeam, awayTeam, matchContext }: MatchDetailBoardProps) {
  const homeStat = getStat(match, match.selecao_home_id)
  const awayStat = getStat(match, match.selecao_away_id)

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(22rem,0.85fr)]">
      <section className="space-y-6">
        <div className="glass-panel rounded-[1.75rem] p-5 sm:p-6">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-full border border-accent/20 bg-accent/8 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-accent">
                  {match.tipo ?? 'Partida'}
                </span>
                <span className="rounded-full border border-line/80 bg-paper/80 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-muted">
                  {match.grupo ?? 'Sem grupo'}
                </span>
                <span className="rounded-full border border-line/80 bg-paper/80 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-muted">
                  Rodada {match.rodada ?? '-'}
                </span>
              </div>

              <div>
                <p className="section-title text-xs text-accent">Detalhe da partida</p>
                <h1 className="mt-2 font-display text-3xl font-semibold text-ink sm:text-4xl">
                  {homeTeam?.name ?? `Seleção ${match.selecao_home_id}`} x {awayTeam?.name ?? `Seleção ${match.selecao_away_id}`}
                </h1>
                <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted">
                  {formatDate(match.data_partida)} • {match.cidade ?? 'Cidade não informada'}
                </p>
              </div>

              <div className="flex flex-wrap items-end gap-4">
                <div className="rounded-[1.5rem] border border-line/80 bg-paper/90 px-5 py-4">
                  <p className="text-xs uppercase tracking-[0.22em] text-muted">Placar final</p>
                  <p className="mt-2 font-display text-4xl font-semibold text-ink">
                    {match.placar_home ?? '—'} <span className="text-accent">x</span> {match.placar_away ?? '—'}
                  </p>
                </div>
                <div className="rounded-[1.5rem] border border-line/80 bg-canvas/60 px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.22em] text-muted">Intervalo</p>
                  <p className="mt-2 font-mono text-lg text-ink">
                    {match.placar_ht_home ?? '—'} x {match.placar_ht_away ?? '—'}
                  </p>
                </div>
                <div className="rounded-[1.5rem] border border-line/80 bg-canvas/60 px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.22em] text-muted">Status</p>
                  <p className="mt-2 font-display text-lg text-ink">{match.status ?? '—'}</p>
                </div>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:min-w-[18rem] lg:grid-cols-1">
              <div className="rounded-[1.5rem] border border-line/80 bg-paper/90 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted">Mandante</p>
                <div className="mt-3 flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-2xl border border-line/70 bg-canvas/60">
                    {homeTeam?.flag_url ? (
                      <Image src={homeTeam.flag_url} alt={homeTeam.name} width={48} height={36} className="h-full w-full object-cover" unoptimized />
                    ) : (
                      <span className="font-display text-sm tracking-[0.25em] text-muted">HM</span>
                    )}
                  </div>
                  <div>
                    <p className="font-display text-lg font-semibold text-ink">{homeTeam?.name ?? 'Casa'}</p>
                    <p className="text-xs uppercase tracking-[0.18em] text-muted">ID {match.selecao_home_id}</p>
                  </div>
                </div>
              </div>

              <div className="rounded-[1.5rem] border border-line/80 bg-paper/90 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted">Visitante</p>
                <div className="mt-3 flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-2xl border border-line/70 bg-canvas/60">
                    {awayTeam?.flag_url ? (
                      <Image src={awayTeam.flag_url} alt={awayTeam.name} width={48} height={36} className="h-full w-full object-cover" unoptimized />
                    ) : (
                      <span className="font-display text-sm tracking-[0.25em] text-muted">AW</span>
                    )}
                  </div>
                  <div>
                    <p className="font-display text-lg font-semibold text-ink">{awayTeam?.name ?? 'Fora'}</p>
                    <p className="text-xs uppercase tracking-[0.18em] text-muted">ID {match.selecao_away_id}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <section className="space-y-4">
          <div className="flex items-end justify-between">
            <h2 className="section-title text-xs text-muted">Comparativo técnico</h2>
            <span className="text-xs uppercase tracking-[0.18em] text-muted">Dados da partida</span>
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
              <p className="section-title text-[10px] text-accent">{homeTeam?.name ?? 'Casa'}</p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <KpiCard label="Posse" value={homeStat?.posse_bola ?? null} unit="%" />
                <KpiCard label="Chutes" value={homeStat?.chutes_total ?? null} unit="" />
                <KpiCard label="No gol" value={homeStat?.chutes_no_gol ?? null} unit="" />
                <KpiCard label="Escanteios" value={homeStat?.escanteios ?? null} unit="" />
                <KpiCard label="Passes certos" value={homeStat?.passes_certos ?? null} unit="" />
                <KpiCard label="Rating" value={homeStat?.performance_rating ?? null} unit="" highlight tone="accent" />
              </div>
            </div>

            <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
              <p className="section-title text-[10px] text-accent">{awayTeam?.name ?? 'Fora'}</p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <KpiCard label="Posse" value={awayStat?.posse_bola ?? null} unit="%" />
                <KpiCard label="Chutes" value={awayStat?.chutes_total ?? null} unit="" />
                <KpiCard label="No gol" value={awayStat?.chutes_no_gol ?? null} unit="" />
                <KpiCard label="Escanteios" value={awayStat?.escanteios ?? null} unit="" />
                <KpiCard label="Passes certos" value={awayStat?.passes_certos ?? null} unit="" />
                <KpiCard label="Rating" value={awayStat?.performance_rating ?? null} unit="" highlight tone="accent" />
              </div>
            </div>
          </div>

          {homeStat && awayStat && (
            <div className="grid gap-4 rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
              <DoubleBar label="Posse de bola" valueA={homeStat.posse_bola ?? 0} valueB={awayStat.posse_bola ?? 0} unit="%" />
              <DoubleBar label="Chutes no gol" valueA={homeStat.chutes_no_gol ?? 0} valueB={awayStat.chutes_no_gol ?? 0} />
              <DoubleBar label="Escanteios" valueA={homeStat.escanteios ?? 0} valueB={awayStat.escanteios ?? 0} />
            </div>
          )}
        </section>

        <section className="space-y-4">
          <div className="flex items-end justify-between">
            <h2 className="section-title text-xs text-muted">Linha do tempo</h2>
            <span className="text-xs uppercase tracking-[0.18em] text-muted">{match.eventos.length} eventos</span>
          </div>

          <div className="space-y-3">
            {match.eventos.length > 0 ? (
              match.eventos.map((event) => {
                const side = event.selecao_id === match.selecao_home_id ? homeTeam?.name ?? 'Casa' : awayTeam?.name ?? 'Fora'
                const minute = event.minuto_extra ? `${event.minuto}'${event.minuto_extra}` : `${event.minuto}'`

                return (
                  <article key={event.id} className="rounded-2xl border border-line/80 bg-paper/90 p-4 shadow-soft">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <div className="flex items-start gap-3">
                        <span className={`rounded-full border px-3 py-1 text-[11px] uppercase tracking-[0.18em] ${eventStyle(event.tipo_evento)}`}>
                          {eventLabel(event.tipo_evento)}
                        </span>
                        <div>
                          <p className="font-medium text-ink">{side}</p>
                          <p className="text-xs uppercase tracking-[0.18em] text-muted">
                            {minute}
                            {event.tipo_gol ? ` • ${event.tipo_gol}` : ''}
                            {event.var_decisao ? ` • VAR ${event.var_decisao}` : ''}
                          </p>
                        </div>
                      </div>
                      <p className="text-sm text-muted">
                        {event.jogador_id ? `Jogador ${event.jogador_id}` : 'Sem jogador'}{' '}
                        {event.assistencia_jogador_id ? ` • Assistência ${event.assistencia_jogador_id}` : ''}
                      </p>
                    </div>
                  </article>
                )
              })
            ) : (
              <div className="rounded-2xl border border-line/80 bg-paper/90 p-5 text-sm text-muted">
                Nenhum evento granular disponível para esta partida.
              </div>
            )}
          </div>
        </section>
      </section>

      <TicketPanel matchContext={matchContext} />
    </div>
  )
}

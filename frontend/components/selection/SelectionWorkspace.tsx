import Image from 'next/image'
import { KpiCard } from '@/components/ui/KpiCard'
import { FormBadge } from '@/components/ui/FormBadge'
import { WindowBadge } from '@/components/ui/WindowBadge'
import { ProgressBar } from '@/components/ui/ProgressBar'
import { MatchHistory } from '@/components/MatchHistory'
import { TicketPanel } from './TicketPanel'
import type { MatchContext, PowerRanking, PlayerItem, SelectionMatchSummary, SelectionStats } from '@/lib/api/types'
import type { Team } from '@/lib/types'

interface SelectionWorkspaceProps {
  team: Team
  stats: SelectionStats
  matches: SelectionMatchSummary[]
  teamNamesById: Map<number, string>
  powerRanking: PowerRanking | null
  players: PlayerItem[]
  matchContext: MatchContext | null
}

function formatMoney(value: number | null, currency: string | null) {
  if (value === null) return '—'
  const formatted = new Intl.NumberFormat('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
  return currency ? `${currency} ${formatted}` : formatted
}

export function SelectionWorkspace({
  team,
  stats,
  matches,
  teamNamesById,
  powerRanking,
  players,
  matchContext,
}: SelectionWorkspaceProps) {
  const form = stats.form_sequence?.split(' ').filter(Boolean) ?? []
  const totalWindow = stats.copa_count + stats.friendly_count

  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.4fr)_minmax(22rem,0.9fr)]">
      <section className="space-y-6">
        <div className="glass-panel rounded-[1.75rem] p-5 sm:p-6">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div className="flex items-start gap-4">
              <div className="flex h-20 w-20 flex-none items-center justify-center overflow-hidden rounded-[1.5rem] border border-line/80 bg-canvas/60 shadow-soft">
                {team.flag_url ? (
                  <Image src={team.flag_url} alt={team.name} width={72} height={54} className="h-full w-full object-cover" unoptimized />
                ) : (
                  <span className="font-display text-xl tracking-[0.3em] text-muted">SM</span>
                )}
              </div>

              <div className="space-y-2">
                <div>
                  <p className="section-title text-xs text-accent">Selecao</p>
                  <h1 className="mt-1 font-display text-3xl font-semibold text-ink">{team.name}</h1>
                </div>
                <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.18em] text-muted">
                  <span className="rounded-full border border-line/80 bg-paper/70 px-3 py-1">Grupo {team.group_name ?? '-'}</span>
                  <span className="rounded-full border border-line/80 bg-paper/70 px-3 py-1">Equipe {team.id}</span>
                  <span className="rounded-full border border-accent/20 bg-accent/8 px-3 py-1 text-accent">{stats.data_quality}</span>
                </div>
                <WindowBadge
                  copaCount={stats.copa_count}
                  friendlyCount={stats.friendly_count}
                  dataQuality={stats.data_quality}
                />
              </div>
            </div>

            <div className="rounded-3xl border border-accent/20 bg-accent/8 px-4 py-4">
              <p className="section-title text-[10px] text-accent-soft">Forma</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {form.length > 0 ? (
                  form.map((result, index) => <FormBadge key={`${team.id}-form-${index}`} result={result as 'V' | 'E' | 'D'} />)
                ) : (
                  <span className="text-sm text-muted">Sem sequencia recente</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {stats.data_quality === 'insufficient' ? (
          <div className="rounded-3xl border border-risk-medium/20 bg-risk-medium/10 p-5">
            <p className="font-display text-lg font-semibold text-ink">Dados insuficientes</p>
            <p className="mt-2 text-sm leading-relaxed text-muted">Menos de 3 jogos estao disponiveis para gerar medias confiaveis.</p>
          </div>
        ) : (
          <>
            {stats.data_quality === 'partial' && (
              <div className="rounded-3xl border border-risk-medium/20 bg-risk-medium/10 px-5 py-3 text-sm text-ink">
                Medias calculadas sobre {totalWindow} jogos da janela atual.
              </div>
            )}

            <section className="space-y-3">
              <div className="flex items-end justify-between">
                <h2 className="section-title text-xs text-muted">Indicadores principais</h2>
                <p className="text-xs uppercase tracking-[0.2em] text-muted">Últimos 5 jogos</p>
              </div>
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                <KpiCard label="Gols marcados" value={stats.avg_goals_scored} unit="/jogo" highlight tone="accent" />
                <KpiCard label="Gols sofridos" value={stats.avg_goals_conceded} unit="/jogo" />
                <KpiCard label="Escanteios" value={stats.avg_corners} unit="/jogo" />
                <KpiCard label="Chutes ao gol" value={stats.avg_shots_on_goal} unit="/jogo" />
                <KpiCard label="Posse de bola" value={stats.avg_possession} unit="%" />
                <KpiCard
                  label="Cartoes"
                  value={
                    stats.avg_yellow_cards !== null && stats.avg_red_cards !== null
                      ? Number((stats.avg_yellow_cards + stats.avg_red_cards).toFixed(2))
                      : null
                  }
                  unit="/jogo"
                />
              </div>
            </section>

            <section className="space-y-4">
              <h2 className="section-title text-xs text-muted">Leitura de apostas</h2>
              <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
                <div className="space-y-4">
                  <ProgressBar label="Over 1.5 gols" value={stats.over15_pct} />
                  <ProgressBar label="Over 2.5 gols" value={stats.over25_pct} />
                  <ProgressBar label="BTTS" value={stats.btts_pct} />
                  <ProgressBar label="Over 3.5 escanteios" value={stats.over35_corners_pct} />
                </div>
              </div>
            </section>

            <section className="space-y-4">
              <h2 className="section-title text-xs text-muted">Tendencia e controle</h2>
              <div className="grid gap-4 md:grid-cols-2">
                <KpiCard label="Gols 1o tempo" value={stats.avg_goals_1h} unit="/jogo" />
                <KpiCard label="Gols 2o tempo" value={stats.avg_goals_2h} unit="/jogo" />
                <KpiCard label="Tendencia de gols" value={stats.trend_goals_3v5} />
                <KpiCard label="Clean sheets" value={stats.clean_sheets} />
              </div>
            </section>

            <details className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
              <summary className="cursor-pointer list-none font-display text-sm uppercase tracking-[0.22em] text-accent">
                Estatisticas completas
              </summary>
              <div className="mt-5 grid gap-5 lg:grid-cols-2">
                <div className="rounded-3xl border border-line/70 bg-canvas/50 p-4">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <KpiCard label="Chutes totais" value={stats.avg_shots_total} unit="/jogo" />
                    <KpiCard label="Chutes dentro" value={stats.avg_shots_inside_box} unit="/jogo" />
                    <KpiCard label="Chutes fora" value={stats.avg_shots_outside_box} unit="/jogo" />
                    <KpiCard label="Chutes bloqueados" value={stats.avg_blocked_shots} unit="/jogo" />
                  </div>
                </div>
                <div className="rounded-3xl border border-line/70 bg-canvas/50 p-4">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <KpiCard label="Passes totais" value={stats.avg_passes_total} unit="/jogo" />
                    <KpiCard label="Passes certos" value={stats.avg_passes_accurate} unit="/jogo" />
                    <KpiCard label="Precisao passes" value={stats.avg_passes_pct} unit="%" />
                    <KpiCard label="Defesas" value={stats.avg_saves} unit="/jogo" />
                  </div>
                </div>
              </div>
            </details>
          </>
        )}

        <section className="space-y-4">
          <div className="flex items-end justify-between">
            <h2 className="section-title text-xs text-muted">Historico recente</h2>
            <span className="text-xs uppercase tracking-[0.18em] text-muted">{matches.length} jogos</span>
          </div>
          <MatchHistory matches={matches} teamId={team.id} teamNamesById={teamNamesById} />
        </section>

        <section className="space-y-4">
          <div className="flex items-end justify-between">
            <h2 className="section-title text-xs text-muted">Ranking e elenco</h2>
            <span className="text-xs uppercase tracking-[0.18em] text-muted">Contexto complementar</span>
          </div>

          <div className="grid gap-4 xl:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
            <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
              <p className="section-title text-[10px] text-accent">Power ranking</p>
              {powerRanking ? (
                <div className="mt-4 space-y-4">
                  <div className="grid gap-3 sm:grid-cols-3">
                    <KpiCard label="Posicao atual" value={powerRanking.rank_atual} tone="accent" />
                    <KpiCard label="Pontos" value={powerRanking.pontos_atuais} />
                    <KpiCard label="Delta" value={powerRanking.rank_diff_ultimo} />
                  </div>
                  <div className="space-y-2">
                    {powerRanking.historico.slice(-4).map((round) => (
                      <div key={`${round.round_id}-${round.rank}`} className="flex items-center justify-between rounded-2xl border border-line/70 bg-canvas/50 px-4 py-3">
                        <div>
                          <p className="text-sm font-medium text-ink">{round.round_nome ?? `Rodada ${round.round_num ?? '-'}`}</p>
                          <p className="text-xs uppercase tracking-[0.18em] text-muted">Round {round.round_id}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-mono text-sm text-accent">#{round.rank}</p>
                          <p className="text-xs text-muted">Pontos {round.pontos ?? '-'}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="mt-3 text-sm text-muted">Nenhum histórico de ranking encontrado.</p>
              )}
            </div>

            <div className="rounded-[1.75rem] border border-line/80 bg-paper/90 p-5 shadow-soft">
              <p className="section-title text-[10px] text-accent">Jogadores</p>
              <div className="mt-4 grid gap-3">
                {players.slice(0, 12).map((player) => (
                  <div key={player.id} className="flex items-center justify-between rounded-2xl border border-line/70 bg-canvas/50 px-4 py-3">
                    <div>
                      <p className="text-sm font-medium text-ink">{player.nome_curto ?? player.nome}</p>
                      <p className="text-xs uppercase tracking-[0.18em] text-muted">
                        {player.posicao ?? '-'} • {player.numero_camisa ?? '-'}
                      </p>
                    </div>
                    <p className="font-mono text-sm text-muted">{formatMoney(player.valor_mercado, player.moeda)}</p>
                  </div>
                ))}
                {players.length === 0 && <p className="text-sm text-muted">Elenco ainda nao carregado.</p>}
              </div>
            </div>
          </div>
        </section>
      </section>

      <TicketPanel matchContext={matchContext} />
    </div>
  )
}

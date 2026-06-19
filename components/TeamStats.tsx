import Image from 'next/image'
import { KpiCard } from './ui/KpiCard'
import { FormBadge } from './ui/FormBadge'
import { WindowBadge } from './ui/WindowBadge'
import { ProgressBar } from './ui/ProgressBar'
import { MatchHistory } from './MatchHistory'
import type { Team, TeamStats as TStats, MatchLog } from '@/lib/types'

interface TeamStatsProps {
  team: Team
  stats: TStats
  matches: MatchLog[]
}

export function TeamStats({ team, stats, matches }: TeamStatsProps) {
  const form = stats.form_sequence?.split(' ').filter(Boolean) ?? []
  const insufficient = stats.data_quality === 'insufficient'
  const partial = stats.data_quality === 'partial'
  const windowSize = stats.copa_count + stats.friendly_count

  return (
    <div className="flex flex-col gap-6 pb-24">
      {/* Header */}
      <div className="flex items-center gap-4">
        {team.flag_url && (
          <Image
            src={team.flag_url}
            alt={team.name}
            width={64}
            height={48}
            className="rounded object-cover"
            unoptimized
          />
        )}
        <div className="flex flex-col gap-1">
          <h1 className="text-text-primary text-2xl font-bold">{team.name}</h1>
          {team.group_name && (
            <span className="text-text-secondary text-sm">Grupo {team.group_name}</span>
          )}
          <WindowBadge
            copaCount={stats.copa_count}
            friendlyCount={stats.friendly_count}
            dataQuality={stats.data_quality}
          />
        </div>
      </div>

      {/* Forma */}
      {form.length > 0 && (
        <div className="flex flex-col gap-2">
          <h2 className="text-text-secondary text-xs uppercase tracking-widest">Forma recente</h2>
          <div className="flex gap-2">
            {form.map((r, i) => (
              <FormBadge key={i} result={r as 'V' | 'E' | 'D'} />
            ))}
          </div>
        </div>
      )}

      {/* KPIs ou aviso */}
      {insufficient ? (
        <div
          className="rounded-lg p-4 text-semantic-amber border border-semantic-amber/30"
          style={{ background: '#1A1A24' }}
        >
          <p className="font-medium">Dados insuficientes</p>
          <p className="text-sm text-text-secondary mt-1">
            Menos de 3 jogos disponíveis. Estatísticas não calculadas.
          </p>
        </div>
      ) : (
        <>
          {partial && (
            <div
              className="rounded-lg px-4 py-2 text-semantic-amber text-sm border border-semantic-amber/30"
              style={{ background: '#1A1A24' }}
            >
              Médias calculadas sobre {windowSize} jogos (janela parcial)
            </div>
          )}

          {/* Grid de KPIs */}
          <div>
            <h2 className="text-text-secondary text-xs uppercase tracking-widest mb-3">Estatísticas médias</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              <KpiCard label="Gols marcados" value={stats.avg_goals_scored} unit="/jogo" highlight />
              <KpiCard label="Gols sofridos" value={stats.avg_goals_conceded} unit="/jogo" />
              <KpiCard label="Escanteios" value={stats.avg_corners} unit="/jogo" />
              <KpiCard label="Cartões" value={
                stats.avg_yellow_cards !== null && stats.avg_red_cards !== null
                  ? Number((stats.avg_yellow_cards! + stats.avg_red_cards!).toFixed(2))
                  : null
              } unit="/jogo" />
              <KpiCard label="Chutes ao gol" value={stats.avg_shots_on_goal} unit="/jogo" />
              <KpiCard label="Posse de bola" value={stats.avg_possession} unit="%" />
            </div>
          </div>

          {/* Indicadores de apostas */}
          <div>
            <h2 className="text-text-secondary text-xs uppercase tracking-widest mb-3">Indicadores</h2>
            <div className="flex flex-col gap-4">
              <ProgressBar label="Over 1.5 gols" value={stats.over15_pct} />
              <ProgressBar label="Over 2.5 gols" value={stats.over25_pct} />
              <ProgressBar label="BTTS (ambos marcam)" value={stats.btts_pct} />
              <ProgressBar label="Over 3.5 escanteios" value={stats.over35_corners_pct} />
            </div>
            <div className="grid grid-cols-2 gap-3 mt-4">
              <KpiCard label="Gols 1º tempo" value={stats.avg_goals_1h} unit="/jogo" />
              <KpiCard label="Gols 2º tempo" value={stats.avg_goals_2h} unit="/jogo" />
            </div>
          </div>

          {/* Stats completas (colapsável) */}
          <details className="group">
            <summary className="cursor-pointer text-neon text-sm py-2 select-none">
              Estatísticas completas ▸
            </summary>
            <div className="grid grid-cols-2 gap-3 mt-3">
              <KpiCard label="Chutes totais" value={stats.avg_shots_total} unit="/jogo" />
              <KpiCard label="Chutes dentro" value={stats.avg_shots_inside_box} unit="/jogo" />
              <KpiCard label="Chutes fora" value={stats.avg_shots_outside_box} unit="/jogo" />
              <KpiCard label="Chutes bloqueados" value={stats.avg_blocked_shots} unit="/jogo" />
              <KpiCard label="Passes totais" value={stats.avg_passes_total} unit="/jogo" />
              <KpiCard label="Passes certos" value={stats.avg_passes_accurate} unit="/jogo" />
              <KpiCard label="Precisão passes" value={stats.avg_passes_pct} unit="%" />
              <KpiCard label="Impedimentos" value={stats.avg_offsides} unit="/jogo" />
              <KpiCard label="Faltas" value={stats.avg_fouls} unit="/jogo" />
              <KpiCard label="Cartões amarelos" value={stats.avg_yellow_cards} unit="/jogo" />
              <KpiCard label="Cartões vermelhos" value={stats.avg_red_cards} unit="/jogo" />
              <KpiCard label="Defesas goleiro" value={stats.avg_saves} unit="/jogo" />
              <KpiCard label="Clean sheets" value={stats.clean_sheets} />
              <KpiCard label="Over 3.5 gols" value={stats.over35_pct} unit="%" />
              <KpiCard label="Tendência gols" value={stats.trend_goals_3v5} />
            </div>
          </details>
        </>
      )}

      {/* Histórico */}
      <div>
        <h2 className="text-text-secondary text-xs uppercase tracking-widest mb-3">
          Histórico de partidas
        </h2>
        <MatchHistory matches={matches} teamId={team.id} />
      </div>
    </div>
  )
}

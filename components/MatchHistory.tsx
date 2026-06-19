import type { MatchLog } from '@/lib/types'

interface MatchHistoryProps {
  matches: MatchLog[]
  teamId: number
}

export function MatchHistory({ matches, teamId }: MatchHistoryProps) {
  if (!matches.length) {
    return <p className="text-text-secondary text-sm">Nenhuma partida encontrada.</p>
  }

  return (
    <div className="flex flex-col gap-2">
      {matches.map((m) => {
        const isHome = true // match_log stores from team perspective
        const homeGoals = m.score_home ?? 0
        const awayGoals = m.score_away ?? 0
        const scoredGoals = homeGoals
        const concededGoals = awayGoals

        let resultColor = 'text-semantic-draw'
        if (scoredGoals > concededGoals) resultColor = 'text-semantic-win'
        if (scoredGoals < concededGoals) resultColor = 'text-semantic-loss'

        return (
          <div
            key={m.match_id}
            className="flex items-center justify-between p-3 rounded-lg"
            style={{ background: '#1A1A24', border: '1px solid #334155' }}
          >
            <div className="flex flex-col gap-0.5">
              <span className="text-text-primary text-sm">vs {m.opponent_name}</span>
              <span className="text-text-secondary text-xs">{m.date}</span>
            </div>
            <div className="flex items-center gap-3">
              <span
                className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  m.match_type === 'Copa'
                    ? 'bg-neon-dark/20 text-neon-light border border-neon-dark/60'
                    : 'bg-text-border/30 text-text-secondary border border-text-border/40'
                }`}
              >
                {m.match_type}
              </span>
              <span className={`font-mono text-base font-bold ${resultColor}`}>
                {m.score_home} – {m.score_away}
              </span>
            </div>
          </div>
        )
      })}
    </div>
  )
}

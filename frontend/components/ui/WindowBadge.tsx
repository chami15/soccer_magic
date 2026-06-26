interface WindowBadgeProps {
  copaCount: number
  friendlyCount: number
  dataQuality?: string
}

export function WindowBadge({ copaCount, friendlyCount, dataQuality }: WindowBadgeProps) {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      {copaCount > 0 && (
        <span className="text-xs px-2 py-0.5 rounded-full bg-neon-dark/20 text-neon-light border border-neon-dark/60">
          {copaCount} Copa
        </span>
      )}
      {friendlyCount > 0 && (
        <span className="text-xs px-2 py-0.5 rounded-full bg-text-border/30 text-text-secondary border border-text-border/40">
          {friendlyCount} Amistoso{friendlyCount > 1 ? 's' : ''}
        </span>
      )}
      {dataQuality === 'partial' && (
        <span className="text-xs px-2 py-0.5 rounded-full bg-semantic-amber/20 text-semantic-amber border border-semantic-amber/40">
          Parcial
        </span>
      )}
    </div>
  )
}

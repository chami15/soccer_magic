interface WindowBadgeProps {
  copaCount: number
  friendlyCount: number
  dataQuality?: string
}

export function WindowBadge({ copaCount, friendlyCount, dataQuality }: WindowBadgeProps) {
  const qualityLabel =
    dataQuality === 'complete' ? 'Janela completa' : dataQuality === 'partial' ? 'Janela parcial' : 'Dados insuficientes'

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="rounded-full border border-line/80 bg-paper/80 px-3 py-1 text-xs text-muted">{qualityLabel}</span>
      <span className="rounded-full border border-accent/20 bg-accent/8 px-3 py-1 text-xs text-accent">{copaCount} Copa</span>
      <span className="rounded-full border border-line/80 bg-paper/80 px-3 py-1 text-xs text-muted">
        {friendlyCount} Amistoso{friendlyCount === 1 ? '' : 's'}
      </span>
    </div>
  )
}

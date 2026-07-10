interface ProgressBarProps {
  label: string
  value: number | null | undefined
  max?: number
}

export function ProgressBar({ label, value, max = 100 }: ProgressBarProps) {
  const pct = value === null || value === undefined ? 0 : Math.min((value / max) * 100, 100)
  const showPositive = pct >= 65

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between gap-3">
        <span className="text-sm text-muted">{label}</span>
        <span className="font-mono text-sm text-ink">{value === null || value === undefined ? '—' : `${value}%`}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-line/70">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${pct}%`,
            background: showPositive
              ? 'linear-gradient(90deg, rgba(192,76,255,0.95), rgba(224,125,255,0.95))'
              : 'linear-gradient(90deg, rgba(150,160,180,0.65), rgba(150,160,180,0.85))',
            boxShadow: showPositive ? '0 0 16px rgba(192,76,255,0.18)' : undefined,
          }}
        />
      </div>
    </div>
  )
}

interface ProgressBarProps {
  label: string
  value: number | null | undefined
  max?: number
}

export function ProgressBar({ label, value, max = 100 }: ProgressBarProps) {
  const pct = value === null || value === undefined ? 0 : Math.min((value / max) * 100, 100)
  const glow = pct > 60

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between items-center">
        <span className="text-sm text-text-secondary">{label}</span>
        <span className="font-mono text-sm text-text-primary">
          {value === null || value === undefined ? '—' : `${value}%`}
        </span>
      </div>
      <div className="h-2 rounded-full bg-bg-elevated overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${pct}%`,
            background: 'linear-gradient(to right, #7C3AED, #A855F7)',
            boxShadow: glow ? '0 0 8px #A855F740' : undefined,
          }}
        />
      </div>
    </div>
  )
}

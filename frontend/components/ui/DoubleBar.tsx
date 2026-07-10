interface DoubleBarProps {
  label: string
  valueA: number | null | undefined
  valueB: number | null | undefined
  unit?: string
  reverse?: boolean
}

function formatValue(value: number | null | undefined, unit?: string) {
  if (value === null || value === undefined) return '—'
  return `${value}${unit ?? ''}`
}

export function DoubleBar({ label, valueA, valueB, unit, reverse = false }: DoubleBarProps) {
  const a = valueA ?? 0
  const b = valueB ?? 0
  const max = Math.max(a, b, 0.01)
  const pctA = (a / max) * 100
  const pctB = (b / max) * 100
  const aWins = reverse ? a < b : a > b
  const bWins = reverse ? b < a : b > a

  return (
    <div className="grid gap-2 py-3">
      <div className="text-center text-[10px] uppercase tracking-[0.22em] text-muted">{label}</div>
      <div className="grid grid-cols-[minmax(3rem,5rem)_1fr_minmax(3rem,5rem)] items-center gap-3">
        <div className={`font-mono text-right text-sm ${aWins ? 'text-accent' : 'text-ink'}`}>{formatValue(valueA, unit)}</div>
        <div className="flex h-2 overflow-hidden rounded-full bg-line/70">
          <div
            className={`h-full rounded-l-full transition-all ${aWins ? 'bg-accent' : 'bg-line/90'}`}
            style={{ width: `${pctA}%` }}
          />
          <div className={`h-full rounded-r-full transition-all ${bWins ? 'bg-accent-soft' : 'bg-line/90'}`} style={{ width: `${pctB}%` }} />
        </div>
        <div className={`font-mono text-sm ${bWins ? 'text-accent' : 'text-ink'}`}>{formatValue(valueB, unit)}</div>
      </div>
    </div>
  )
}

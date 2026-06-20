interface DoubleBarProps {
  label: string
  valueA: number | null | undefined
  valueB: number | null | undefined
  unit?: string
}

export function DoubleBar({ label, valueA, valueB, unit }: DoubleBarProps) {
  const a = valueA ?? 0
  const b = valueB ?? 0
  const max = Math.max(a, b, 0.01)
  const pctA = (a / max) * 100
  const pctB = (b / max) * 100
  const aWins = a > b
  const bWins = b > a

  const fmt = (v: number | null | undefined) =>
    v === null || v === undefined ? '—' : `${v}${unit ? unit : ''}`

  return (
    <div className="py-2">
      <div className="text-xs text-text-secondary text-center mb-1.5">{label}</div>
      <div className="flex items-center gap-2">
        <span className={`font-mono text-sm w-12 text-right ${aWins ? 'text-neon font-bold' : 'text-text-primary'}`}>
          {fmt(valueA)}
        </span>
        <div className="flex-1 flex gap-1 h-2">
          <div className="flex-1 flex justify-end">
            <div
              className="h-full rounded-l-full"
              style={{
                width: `${pctA}%`,
                background: aWins ? 'linear-gradient(to left, #7C3AED, #A855F7)' : '#334155',
              }}
            />
          </div>
          <div className="flex-1">
            <div
              className="h-full rounded-r-full"
              style={{
                width: `${pctB}%`,
                background: bWins ? 'linear-gradient(to right, #7C3AED, #A855F7)' : '#334155',
              }}
            />
          </div>
        </div>
        <span className={`font-mono text-sm w-12 ${bWins ? 'text-neon font-bold' : 'text-text-primary'}`}>
          {fmt(valueB)}
        </span>
      </div>
    </div>
  )
}

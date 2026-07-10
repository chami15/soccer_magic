interface KpiCardProps {
  label: string
  value: string | number | null | undefined
  unit?: string
  highlight?: boolean
  tone?: 'neutral' | 'accent' | 'positive' | 'warning'
}

export function KpiCard({ label, value, unit, highlight = false, tone = 'neutral' }: KpiCardProps) {
  const display = value === null || value === undefined ? '—' : value

  const toneStyles = {
    neutral: 'border-line/80 bg-paper/85',
    accent: 'border-accent/25 bg-paper/88',
    positive: 'border-risk-low/25 bg-paper/85',
    warning: 'border-risk-medium/25 bg-paper/85',
  }

  return (
    <div className={`rounded-2xl border p-4 transition-transform duration-200 hover:-translate-y-0.5 ${toneStyles[tone]} shadow-soft`}>
      <div className="mb-3 flex items-center justify-between">
        <span className="section-title text-[10px] text-muted">{label}</span>
        {highlight && <span className="h-2 w-2 rounded-full bg-accent shadow-[0_0_0_6px_rgba(192,76,255,0.12)]" />}
      </div>
      <div className={`font-mono text-2xl font-semibold ${highlight ? 'text-accent' : 'text-ink'}`}>
        {display}
        {unit && <span className="ml-2 text-sm font-normal text-muted">{unit}</span>}
      </div>
    </div>
  )
}

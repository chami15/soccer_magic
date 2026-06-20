interface KpiCardProps {
  label: string
  value: string | number | null | undefined
  unit?: string
  highlight?: boolean
}

export function KpiCard({ label, value, unit, highlight = false }: KpiCardProps) {
  const display = value === null || value === undefined ? '—' : value

  return (
    <div
      className="rounded-lg p-4 flex flex-col gap-1"
      style={{
        background: '#1A1A24',
        border: '1px solid rgba(124,58,237,0.25)',
        borderTop: '2px solid #A855F7',
        boxShadow: '0 0 16px rgba(168,85,247,0.08)',
      }}
    >
      <span className="text-xs text-text-secondary uppercase tracking-wide">{label}</span>
      <span className={`font-mono text-2xl font-semibold ${highlight ? 'text-neon' : 'text-text-primary'}`}>
        {display}
        {unit && <span className="text-sm text-text-secondary ml-1">{unit}</span>}
      </span>
    </div>
  )
}

interface FormBadgeProps {
  result: 'V' | 'E' | 'D'
}

const styles = {
  V: 'border-risk-low/30 bg-risk-low/12 text-risk-low',
  E: 'border-risk-medium/30 bg-risk-medium/12 text-risk-medium',
  D: 'border-risk-high/30 bg-risk-high/12 text-risk-high',
}

export function FormBadge({ result }: FormBadgeProps) {
  return (
    <span className={`inline-flex h-8 w-8 items-center justify-center rounded-full border text-[11px] font-semibold ${styles[result]}`}>
      {result}
    </span>
  )
}

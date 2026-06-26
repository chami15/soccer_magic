interface FormBadgeProps {
  result: 'V' | 'E' | 'D'
}

const styles = {
  V: 'bg-semantic-win/20 text-semantic-win border border-semantic-win/40',
  E: 'bg-semantic-draw/20 text-semantic-draw border border-semantic-draw/40',
  D: 'bg-semantic-loss/20 text-semantic-loss border border-semantic-loss/40',
}

export function FormBadge({ result }: FormBadgeProps) {
  return (
    <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold font-mono ${styles[result]}`}>
      {result}
    </span>
  )
}

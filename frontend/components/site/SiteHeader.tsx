'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const links = [
  { href: '/', label: 'Selecoes' },
  { href: '/matches', label: 'Calendario' },
  { href: '/simulate', label: 'Comparador' },
  { href: '/pipeline', label: 'Pipeline' },
]

export function SiteHeader() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-40 border-b border-line/70 bg-canvas/85 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-accent/20 bg-paper/80 text-accent shadow-soft">
            <span className="font-display text-sm font-semibold tracking-[0.3em]">SM</span>
          </div>
          <div>
            <p className="font-display text-base font-semibold tracking-[0.18em] text-ink">
              Soccer Magic
            </p>
            <p className="text-xs uppercase tracking-[0.28em] text-muted">Copa 2026</p>
          </div>
        </div>

        <nav className="flex items-center gap-1 overflow-x-auto rounded-full border border-line/70 bg-paper/60 p-1">
          {links.map((link) => {
            const active = pathname === link.href || (link.href !== '/' && pathname.startsWith(link.href))

            return (
              <Link
                key={link.href}
                href={link.href}
                className={[
                  'rounded-full px-4 py-2 text-xs uppercase tracking-[0.22em] transition-all',
                  active
                    ? 'bg-accent text-white shadow-soft'
                    : 'text-muted hover:bg-paper hover:text-ink',
                ].join(' ')}
              >
                {link.label}
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}

'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const links = [
  { href: '/', label: 'Seleções', icon: '🏆' },
  { href: '/matches', label: 'Calendário', icon: '📅' },
  { href: '/simulate', label: 'Simular', icon: '⚔️' },
  { href: '/pipeline', label: 'Pipeline', icon: '⚙️' },
]

export function SideNav() {
  const pathname = usePathname()

  return (
    <nav
      className="hidden lg:flex fixed left-0 top-0 h-screen w-60 flex-col z-50 border-r border-text-border/30"
      style={{ background: '#111118' }}
    >
      {/* Logo */}
      <div className="px-6 py-6 border-b border-text-border/30">
        <span className="text-xl font-bold">
          <span className="text-neon">Soccer</span>{' '}
          <span className="text-text-primary">Magic</span>
        </span>
        <p className="text-xs text-text-secondary mt-0.5">Copa do Mundo 2026</p>
      </div>

      {/* Links */}
      <div className="flex flex-col gap-1 px-3 py-4 flex-1">
        {links.map(({ href, label, icon }) => {
          const active = pathname === href || (href !== '/' && pathname.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? 'text-neon bg-neon-dark/10 border border-neon-dark/20'
                  : 'text-text-secondary hover:text-text-primary hover:bg-bg-elevated'
              }`}
            >
              <span className="text-base">{icon}</span>
              {label}
            </Link>
          )
        })}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-text-border/30">
        <p className="text-xs text-text-secondary">v2.0 · Sofascore</p>
      </div>
    </nav>
  )
}

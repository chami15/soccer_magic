'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const links = [
  { href: '/', label: 'Seleções', icon: '🏆' },
  { href: '/simulate', label: 'Simular', icon: '⚔️' },
  { href: '/pipeline', label: 'Pipeline', icon: '⚙️' },
]

export function BottomNav() {
  const pathname = usePathname()

  return (
    <nav
      className="lg:hidden fixed bottom-0 left-0 right-0 z-50 border-t border-text-border"
      style={{ background: '#111118' }}
    >
      <div className="max-w-screen-sm mx-auto flex">
        {links.map(({ href, label, icon }) => {
          const active = pathname === href || (href !== '/' && pathname.startsWith(href))
          return (
            <Link
              key={href}
              href={href}
              className={`flex-1 flex flex-col items-center py-3 gap-1 text-xs transition-colors ${
                active ? 'text-neon' : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              <span className="text-lg">{icon}</span>
              {label}
            </Link>
          )
        })}
      </div>
    </nav>
  )
}

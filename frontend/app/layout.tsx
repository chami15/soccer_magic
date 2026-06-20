import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { BottomNav } from '@/components/BottomNav'
import { SideNav } from '@/components/SideNav'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' })

export const metadata: Metadata = {
  title: 'Soccer Magic — Copa 2026',
  description: 'Análise estatística das 48 seleções da Copa do Mundo FIFA 2026',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="bg-bg-base text-text-primary font-sans antialiased pb-16 lg:pb-0 lg:pl-60">
        <SideNav />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 min-h-screen">
          {children}
        </main>
        <BottomNav />
      </body>
    </html>
  )
}

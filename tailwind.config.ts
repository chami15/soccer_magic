import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: {
          base:     '#0A0A0F',
          surface:  '#111118',
          elevated: '#1A1A24',
        },
        neon: {
          DEFAULT: '#A855F7',
          light:   '#C084FC',
          dark:    '#7C3AED',
        },
        text: {
          primary:   '#F8FAFC',
          secondary: '#94A3B8',
          border:    '#334155',
        },
        semantic: {
          win:   '#22C55E',
          draw:  '#EAB308',
          loss:  '#EF4444',
          amber: '#F59E0B',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        neon:      '0 0 16px #A855F715',
        'neon-sm': '0 0 8px #A855F740',
      },
    },
  },
  plugins: [],
}

export default config

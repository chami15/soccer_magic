import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: 'var(--color-canvas)',
        paper: 'var(--color-paper)',
        surface: 'var(--color-surface)',
        elevated: 'var(--color-elevated)',
        ink: 'var(--color-ink)',
        muted: 'var(--color-muted)',
        line: 'var(--color-line)',
        accent: {
          DEFAULT: 'var(--color-accent)',
          soft: 'var(--color-accent-soft)',
          deep: 'var(--color-accent-deep)',
        },
        risk: {
          low: 'var(--color-risk-low)',
          medium: 'var(--color-risk-medium)',
          high: 'var(--color-risk-high)',
        },
        semantic: {
          win: 'var(--color-win)',
          draw: 'var(--color-draw)',
          loss: 'var(--color-loss)',
          amber: 'var(--color-amber)',
        },
        bg: {
          base: 'var(--color-canvas)',
          surface: 'var(--color-paper)',
          elevated: 'var(--color-elevated)',
        },
        neon: {
          DEFAULT: 'var(--color-accent)',
          light: 'var(--color-accent-soft)',
          dark: 'var(--color-accent-deep)',
        },
        text: {
          primary: 'var(--color-ink)',
          secondary: 'var(--color-muted)',
          border: 'var(--color-line)',
        },
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'sans-serif'],
        display: ['var(--font-display)', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      boxShadow: {
        soft: '0 14px 40px rgba(0, 0, 0, 0.18)',
        lift: '0 8px 18px rgba(0, 0, 0, 0.14)',
      },
      borderRadius: {
        xl2: '1.25rem',
      },
    },
  },
  plugins: [],
}

export default config

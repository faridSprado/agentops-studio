import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
        display: ['var(--font-sans)', 'system-ui', 'sans-serif']
      },
      colors: {
        ink: {
          DEFAULT: '#0a0908',
          soft: '#100f0e',
          muted: '#1a1917'
        },
        surface: {
          DEFAULT: '#161412',
          raised: '#1e1c19',
          hover: '#262320'
        },
        line: {
          DEFAULT: '#2e2b28',
          soft: '#3d3935'
        },
        cream: {
          DEFAULT: '#f5f0e8',
          muted: '#c9c2b8',
          dim: '#8a837a'
        },
        brand: {
          DEFAULT: '#d4715c',
          light: '#e8957f',
          dark: '#b85a47',
          glow: 'rgba(212, 113, 92, 0.35)'
        },
        sage: {
          DEFAULT: '#7d9b8a',
          light: '#9bb8a8',
          muted: 'rgba(125, 155, 138, 0.15)'
        },
        gold: {
          DEFAULT: '#c9a962',
          muted: 'rgba(201, 169, 98, 0.12)'
        }
      },
      borderRadius: {
        sm: '0.5rem',
        md: '0.75rem',
        lg: '1rem',
        xl: '1.25rem',
        '2xl': '1.5rem',
        card: '1.25rem',
        pill: '9999px'
      },
      boxShadow: {
        soft: '0 2px 20px rgba(0, 0, 0, 0.25)',
        panel: '0 8px 40px rgba(0, 0, 0, 0.35)',
        glow: '0 0 48px var(--brand-glow)',
        inset: 'inset 0 1px 0 rgba(255, 255, 255, 0.04)'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        shimmer: 'shimmer 2s ease-in-out infinite',
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards'
      },
      keyframes: {
        shimmer: {
          '0%, 100%': { opacity: '0.35' },
          '50%': { opacity: '0.7' }
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' }
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(16px)' },
          to: { opacity: '1', transform: 'translateY(0)' }
        }
      },
      backgroundImage: {
        'grain': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E\")"
      }
    }
  },
  plugins: []
};

export default config;

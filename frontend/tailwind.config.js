/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: 'var(--orange-light)',
          100: 'var(--orange-light)',
          200: 'var(--orange-mid)',
          300: '#fdba74', // fallback/intermediate
          400: '#fb923c', // fallback/intermediate
          500: 'var(--orange)',
          600: 'var(--orange2)',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
        },
        orange: {
          50: 'var(--orange-light)',
          100: 'var(--orange-mid)',
          200: '#fdba74',
          300: '#fb923c',
          400: '#f7944d',
          500: 'var(--orange)',
          600: 'var(--orange2)',
          700: '#c2410c',
          800: '#a33d07',
          900: '#7c2d12',
        },
        slate: {
          50: 'var(--surface2)',
          100: 'var(--bg)',
          200: 'var(--border)',
          300: 'var(--border2)',
          400: 'var(--text2)',
          500: 'var(--text2)',
          600: 'var(--text2)',
          700: 'var(--text)',
          800: 'var(--text)',
          900: 'var(--text)',
        },
        green: 'var(--green)',
        yellow: 'var(--yellow)',
        red: 'var(--red)',
        blue: 'var(--blue)',
      },

      boxShadow: {
        'sm': 'var(--shadow-sm)',
        'DEFAULT': 'var(--shadow)',
        'lg': 'var(--shadow-lg)',
        subtle: '0 10px 30px -20px rgba(15, 23, 42, 0.35)',
        card: '0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.1), 0 8px 24px rgba(0,0,0,0.06)',
      },
      keyframes: {
        'highlight-pulse': {
          '0%, 100%': { backgroundColor: 'transparent' },
          '50%': { backgroundColor: 'rgb(219 234 254)' },
        },
        'highlight-in': {
          '0%': { backgroundColor: 'transparent' },
          '100%': { backgroundColor: 'rgb(219 234 254)' },
        },
        'scan-horizontal': {
          '0%': { left: '-10%', opacity: '0' },
          '5%': { opacity: '1' },
          '95%': { opacity: '1' },
          '100%': { left: '110%', opacity: '0' },
        },
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-left': {
          '0%': { opacity: '0', transform: 'translateX(-16px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
      animation: {
        'highlight-pulse': 'highlight-pulse 1.5s ease-in-out 2',
        'highlight-in': 'highlight-in 0.4s ease-out forwards',
        scan: 'scan-horizontal 3s linear infinite',
        'fade-in': 'fade-in 0.4s ease-out forwards',
        'slide-in-left': 'slide-in-left 0.3s ease-out forwards',
      },
      backgroundImage: {
        'sidebar-gradient': 'linear-gradient(135deg, #fff4eb 0%, #fde8d4 50%, #ffffff 100%)',
        'header-gradient': 'linear-gradient(90deg, #f47920 0%, #e05c0a 100%)',
        'card-gradient': 'linear-gradient(135deg, #fff4eb 0%, #ffffff 100%)',
        'accent-gradient': 'linear-gradient(135deg, #f47920 0%, #fb923c 100%)',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

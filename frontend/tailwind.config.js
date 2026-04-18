/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
          navy: '#1a2340',
        },
        teal: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
        slate: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#5c6b8c',
          600: '#415173',
          700: '#2d3b5c',
          800: '#1a2340',
          900: '#0e1324',
        },
      },
      boxShadow: {
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
        'sidebar-gradient': 'linear-gradient(135deg, #f5f3ff 0%, #e0f2fe 50%, #f0fdfa 100%)',
        'header-gradient': 'linear-gradient(90deg, #7c3aed 0%, #14b8a6 100%)',
        'card-gradient': 'linear-gradient(135deg, #f8fafc 0%, #f0fdfa 100%)',
        'accent-gradient': 'linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%)',
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

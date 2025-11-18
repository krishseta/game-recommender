/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Deep dark mode palette
        'charcoal': {
          950: '#0a0a0f',
          900: '#12121a',
          800: '#1a1a24',
          700: '#22222e',
          600: '#2a2a38',
        },
        'slate': {
          700: '#3a3a4a',
          600: '#4a4a5a',
          500: '#5a5a6a',
        },
        // Elegant neon accents
        'cyan': {
          400: '#22d3ee',
          500: '#06b6d4',
        },
        'amber': {
          400: '#fbbf24',
          500: '#f59e0b',
        },
      },
      fontFamily: {
        'display': ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'mist': 'mist 30s ease-in-out infinite',
        'particle': 'particle 25s linear infinite',
        'float-slow': 'floatSlow 8s ease-in-out infinite',
        'fade-in': 'fadeIn 0.8s ease-out',
        'modal-in': 'modalIn 0.4s cubic-bezier(0.22, 1, 0.36, 1)',
      },
      keyframes: {
        mist: {
          '0%, 100%': { 
            transform: 'translate(0, 0) scale(1)',
            opacity: '0.03'
          },
          '50%': { 
            transform: 'translate(50px, -30px) scale(1.2)',
            opacity: '0.05'
          },
        },
        particle: {
          '0%': { 
            transform: 'translateY(0) translateX(0)',
            opacity: '0'
          },
          '10%': { opacity: '0.3' },
          '90%': { opacity: '0.3' },
          '100%': { 
            transform: 'translateY(-100vh) translateX(50px)',
            opacity: '0'
          },
        },
        floatSlow: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        modalIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      backdropBlur: {
        'xs': '2px',
        'ultra': '40px',
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.05)',
        'depth': '0 30px 80px rgba(0, 0, 0, 0.6), 0 10px 30px rgba(0, 0, 0, 0.4)',
        'modal': '0 40px 100px rgba(0, 0, 0, 0.8)',
      },
    },
  },
  plugins: [],
}

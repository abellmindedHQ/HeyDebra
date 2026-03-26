/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'deep-black': '#080808',
        'hot-pink': '#FF006E',
        'fuchsia': '#FF2D78',
        'gold': '#FFD700',
        'gold-dim': '#C9A227',
        'teal': '#00F5FF',
        'teal-dim': '#00B4C8',
        'dark-surface': '#111111',
        'dark-card': '#181818',
        'dark-border': '#2A2A2A',
      },
      fontFamily: {
        'display': ['Bebas Neue', 'Impact', 'Arial Black', 'sans-serif'],
        'body': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Courier New', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'hero-glow': 'radial-gradient(ellipse at center, rgba(255,0,110,0.15) 0%, rgba(0,245,255,0.05) 50%, transparent 70%)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'scan': 'scan 3s linear infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        glow: {
          'from': { textShadow: '0 0 20px #FF006E, 0 0 40px #FF006E' },
          'to': { textShadow: '0 0 40px #FF006E, 0 0 80px #FF006E, 0 0 120px #FF006E' },
        },
      },
    },
  },
  plugins: [],
}

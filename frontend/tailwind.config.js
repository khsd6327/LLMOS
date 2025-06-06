/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',  // ← 이 부분이 빠져있었음
  theme: {
    extend: {
      colors: {
        'claude-orange': '#ff6b35',
        'claude-blue': '#4f46e5',
        dark: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617'
        }
      }
    },
  },
  plugins: [],
}

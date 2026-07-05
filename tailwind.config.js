export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Bricolage Grotesque"', 'serif'],
        body: ['"Manrope"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace']
      },
      colors: {
        volt: {
          night: '#061014',
          panel: '#0b1820',
          mint: '#36f69a',
          cyan: '#4cc9ff',
          blue: '#2777ff',
          amber: '#ffd267'
        }
      }
    }
  },
  plugins: []
};

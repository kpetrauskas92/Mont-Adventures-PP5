/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',        // Global templates in root
    './**/templates/**/*.html'      // Templates in each app
  ],
  theme: {
    fontFamily: {
      'sans': ['Rubik', 'ui-sans-serif', 'system-ui'],
      'serif': ['ui-serif', 'Georgia'],
      'mono': ['ui-monospace', 'SFMono-Regular'],
      'display': ['Rubik'],
      'body': ['"sans-serif"'],
    },
    extend: {},
  },
  plugins: [require("daisyui")],

  daisyui: {
    themes: [
      {
        mytheme: {
        


"primary": "#242424",
        


"secondary": "#d9864b",
        


"accent": "#379673",
        


"neutral": "#e6e8ea",
        


"base-100": "#ffffff",
        


"info": "#65c6e7",
        


"success": "#33cc7d",
        


"warning": "#e5b90b",
        


"error": "#e4321b",
        },
      },
    ],
  },
}
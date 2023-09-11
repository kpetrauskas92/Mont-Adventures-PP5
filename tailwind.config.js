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
    themes: ["light", "dark", "cupcake"],
    darkTheme: "dark",
    base: true,
    styled: true,
    utils: true,
    rtl: false,
    prefix: "",
    logs: true,
  },
}
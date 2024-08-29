/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/static/**/*.js',
  ],
  theme: {
    extend: {},
  },
  daisyui: {
    themes: [
      {
        dark: {
          "primary": "#21B356",
          "secondary": "#00faf0",
          "accent": "#ce4600",
          "neutral": "#1C1917",
          "base-100": "#202020",
          "info": "#00c7ff",
          "success": "#21B356",
          "warning": "#ffad00",
          "error": "#ff536b",
        },
      },
    ],
  },
  plugins: [
    // ...
    require('daisyui'),
    require('@tailwindcss/forms'),
  ],
}  // tailwind.config.js
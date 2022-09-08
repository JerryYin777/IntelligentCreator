/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/views/**/*.vue',
    './src/App.vue',
  ],
  theme: {
    extend: {
      colors: {
        orange: {
          50: '#fff6ed',
          100: '#ffebd4',
          200: '#ffd3a9',
          300: '#ffa456',
          400: '#fe8a00',
          500: '#fc6613',
          600: '#ed4c09',
          700: 'c53709',
          800: '#9c2c10',
          900: '#7e2710',
        },
        indigo:{
          50: '#faf5ff',
          100: '#f3e9fe',
          200: '#e9d6fe',
          300: '#d9b7fb',
          400: '#c188f8',
          500: '#aa5bf1',
          600: '#8e2de2',
          700: '#8028c8',
          800: '#6c26a3',
          900: '#592083',
        },
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}

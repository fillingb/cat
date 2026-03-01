/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'xhs': {
          pink: '#FF2442',
          soft: '#FF4D6D',
          light: '#FFF1F2',
          cream: '#FFF9F0',
        }
      },
      borderRadius: {
        '4xl': '2rem',
        '5xl': '3rem',
      },
      fontFamily: {
        sans: ['"Noto Sans SC"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

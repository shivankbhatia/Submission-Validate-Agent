/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#FF8C42",
        secondary: "#FF6B35",
        accent: "#FFF5EE",
        dark: "#2C1810",
        orange: {
          50: "#FFF5EE",
          100: "#FFE8D9",
          200: "#FFD1B3",
          300: "#FFBA8C",
          400: "#FFA366",
          500: "#FF8C42",
          600: "#FF6B35",
          700: "#E65100",
          800: "#BF360C",
          900: "#8D2600",
        }
      }
    },
  },
  plugins: [],
}


// colors: {
//   primary: "#0A66C2",
//   secondary: "#0073B1",
//   accent: "#F3F4F6",
//   dark: "#101820",
// }
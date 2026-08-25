/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["IBM Plex Sans", "Segoe UI", "sans-serif"],
        display: ["Fraunces", "Georgia", "serif"],
      },
      colors: {
        canopy: {
          50: "#f3f7f4",
          100: "#e4eee6",
          800: "#1e3a2f",
          900: "#12241c",
          950: "#0b1612",
        },
      },
    },
  },
  plugins: [],
};

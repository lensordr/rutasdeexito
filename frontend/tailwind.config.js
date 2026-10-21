/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Red brand ramp
        brand: {
          50: "#fff1f1",
          100: "#ffdede",
          200: "#ffc2c2",
          300: "#ff9898",
          400: "#ff5a5a",
          500: "#f21b1b",
          600: "#dc0d0d",
          700: "#b80909",
          800: "#8f0808",
          900: "#5c0404",
        },
        // Near-black ink ramp
        ink: {
          900: "#0a0a0a",
          800: "#121212",
          700: "#1a1a1a",
          600: "#232323",
          500: "#2e2e2e",
          400: "#3a3a3a",
        },
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(220,13,13,0.25), 0 8px 30px rgba(0,0,0,0.5)",
      },
    },
  },
  plugins: [],
};

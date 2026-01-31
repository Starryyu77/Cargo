/** @type {import('tailwindcss').Config} */

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    container: {
      center: true,
    },
    extend: {
      colors: {
        crt: {
          green: "#33ff33",
          "green-dim": "#1a801a",
          "green-dark": "#0d400d",
          black: "#0a0a0a",
          scanline: "rgba(0, 0, 0, 0.5)",
        },
      },
      fontFamily: {
        mono: ['"VT323"', "monospace"],
      },
      animation: {
        "crt-flicker": "flicker 0.15s infinite",
        "scanline": "scanline 8s linear infinite",
      },
      keyframes: {
        flicker: {
          "0%": { opacity: "0.97" },
          "5%": { opacity: "0.95" },
          "10%": { opacity: "0.9" },
          "15%": { opacity: "0.95" },
          "20%": { opacity: "0.99" },
          "50%": { opacity: "0.95" },
          "80%": { opacity: "0.9" },
          "100%": { opacity: "0.95" },
        },
        scanline: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" },
        },
      },
    },
  },
  plugins: [],
};

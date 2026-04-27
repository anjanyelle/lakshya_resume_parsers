/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#faf5ff",
          100: "#f3e8ff",
          200: "#e9d5ff",
          300: "#d8b4fe",
          400: "#c084fc",
          500: "#a855f7",
          600: "#9333ea",
          700: "#7e22ce",
          800: "#6b21a8",
          900: "#581c87",
        },
        slate: {
          50: "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          800: "#1f2937",
          900: "#0f172a",
        },
      },
      boxShadow: {
        subtle: "0 10px 30px -20px rgba(15, 23, 42, 0.35)",
      },
      keyframes: {
        "highlight-pulse": {
          "0%, 100%": { backgroundColor: "transparent" },
          "50%": { backgroundColor: "rgb(219 234 254)" },
        },
        "highlight-in": {
          "0%": { backgroundColor: "transparent" },
          "100%": { backgroundColor: "rgb(219 234 254)" },
        },
        "scan-horizontal": {
          "0%": { left: "-10%", opacity: "0" },
          "5%": { opacity: "1" },
          "95%": { opacity: "1" },
          "100%": { left: "110%", opacity: "0" },
        },
      },
      animation: {
        "highlight-pulse": "highlight-pulse 1.5s ease-in-out 2",
        "highlight-in": "highlight-in 0.4s ease-out forwards",
        scan: "scan-horizontal 3s linear infinite",
      },
    },
  },
  plugins: [],
};

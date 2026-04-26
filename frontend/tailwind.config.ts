import type { Config } from "tailwindcss";

export default {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0D0D0D",
        secondary: "#1A1A1A",
        card: "#21262D",
        hover: "#292E36",
        "accent-gold": "#C9A962",
        "accent-gold-dim": "#A68B4B",
        "accent-blue": "#4A9EFF",
        "accent-red": "#F07178",
        "accent-green": "#56D364",
        "accent-purple": "#A371F7",
        "accent-orange": "#FFA657",
        "accent-cyan": "#39C5CF",
        border: "#30363D",
        "text-primary": "#E6EDF3",
        "text-secondary": "#8B949E",
        "text-muted": "#6E7681",
      },
      fontFamily: {
        sans: ["Noto Sans SC", "Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;

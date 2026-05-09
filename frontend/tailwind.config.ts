import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#101418",
        mist: "#f3f6f8",
        coral: "#ff5a36",
        jade: "#0f766e",
        saffron: "#f59e0b",
      },
      boxShadow: {
        card: "0 18px 40px rgba(15, 23, 42, 0.09)",
      },
    },
  },
  plugins: [],
};

export default config;

import sharedConfig from "../../packages/ui/tailwind.config.js";

/** @type {import('tailwindcss').Config} */
export default {
  ...sharedConfig,
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "../../packages/ui/src/**/*.{js,ts,jsx,tsx}",
  ],
  // Extend or override theme if needed, but presets handle most
};

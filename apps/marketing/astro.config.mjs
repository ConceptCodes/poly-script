// @ts-check
import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  integrations: [tailwind()],
  i18n: {
    defaultLocale: "en",
    locales: ["en", "de", "es", "fr", "jp"],
  },
});

// @ts-check
// TODO: Install @astrojs/mdx to enable MDX content support
import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  integrations: [tailwind()],
  i18n: {
    defaultLocale: "en",
    locales: ["en", "de", "es", "fr", "jp"],
  },
  site: "https://polyscript.io",
});

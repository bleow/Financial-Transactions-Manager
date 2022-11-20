//used for building and using live reload for development

import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  define: {
    // https://github.com/permafrost-dev/vue-ray/issues/3
    global: {},
    'process.env': process.env
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
      './runtimeConfig': './runtimeConfig.browser',
    },
  },
});

// Vite web builder configuration file.
//
// For more information, visit https://vitejs.dev/config.
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "url";
import { defineConfig } from "vite";

export default defineConfig({
  build: {
    outDir: "../../dist",
  },
  plugins: [vue()],
  publicDir: "../public",
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("frontend/src", import.meta.url)),
    },
  },
  root: "frontend/src",
});

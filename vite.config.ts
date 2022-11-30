// Vite web builder configuration file.
//
// For more information, visit https://vitejs.dev/config.
import vue from "@vitejs/plugin-vue";
import { visualizer } from "rollup-plugin-visualizer";
import { fileURLToPath, URL } from "url";
import { defineConfig } from "vite";

export default defineConfig({
  build: {
    emptyOutDir: true,
    outDir: "../../backend/acronyms/web",
  },
  // Rollup plugin visualizer should be the last plugin.
  plugins: [vue(), visualizer()],
  publicDir: "../public",
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("frontend/src", import.meta.url)),
    },
  },
  root: "frontend/src",
});

// Vite web builder configuration file.
//
// For more information, visit https://vitejs.dev/config.
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "url";
import { defineConfig } from "vite";
import { visualizer } from "rollup-plugin-visualizer";

export default defineConfig({
  build: {
    emptyOutDir: true,
    outDir: "../../dist",
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

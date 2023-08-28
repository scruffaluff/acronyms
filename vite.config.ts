// Vite web builder configuration file.
//
// For more information, visit https://vitejs.dev/config.
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";
import { visualizer } from "rollup-plugin-visualizer";
import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  build: {
    emptyOutDir: false,
    outDir: "../acronyms/web",
  },
  // Rollup plugin visualizer should be the last plugin.
  plugins: [vue(), visualizer()],
  publicDir: "../../assets",
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("src/frontend", import.meta.url)),
    },
  },
  root: "src/frontend",
});

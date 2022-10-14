// Vite web builder configuration file.
//
// For more information, visit https://vitejs.dev/config.

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  publicDir: "frontend/public",
});

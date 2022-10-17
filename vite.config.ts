// Vite web builder configuration file.
//
// For more information, visit https://vitejs.dev/config.
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [vue()],
  publicDir: "frontend/public",
});

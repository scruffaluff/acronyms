// <reference types="vitest" />
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  publicDir: "frontend/public",
  test: {
    include: ["tests/frontend/**/*.test.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"],
  },
});

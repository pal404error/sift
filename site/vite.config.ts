import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages serves project sites under /sift/, so use relative base paths.
export default defineConfig({
  base: "./",
  plugins: [react()],
  build: {
    outDir: "dist",
    assetsDir: "assets",
    emptyOutDir: true,
  },
});

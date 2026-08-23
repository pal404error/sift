import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server proxies API calls to the running Sift FastAPI backend so the SPA can
// call /search and /ask/stream on the same origin during development. Override with
// `SIFT_API_URL=http://host:port npm run dev` if your backend isn't on :8000.
const API_TARGET = "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "/search": { target: API_TARGET, changeOrigin: true },
      "/ask": { target: API_TARGET, changeOrigin: true },
      "/crawl": { target: API_TARGET, changeOrigin: true },
      "/health": { target: API_TARGET, changeOrigin: true },
    },
  },
});

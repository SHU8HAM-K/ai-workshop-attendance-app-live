/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { VitePWA } from "vite-plugin-pwa";
import path from "node:path";

// Where the API lives during development. Inside the docker dev stack the
// backend is reachable by service name; running `npm run dev` on the host it is
// on localhost. Production never uses this — FastAPI serves the built SPA from
// its own origin, so /api is same-origin and no proxy exists.
const apiTarget = process.env.VITE_API_PROXY ?? "http://localhost:8000";

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    // Installable app + offline shell. The service worker is generated at build
    // time only; `npm run dev` never registers one, so hot reload is unaffected.
    VitePWA({
      // A new deploy takes over on the next load, with no "refresh?" prompt.
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg", "apple-touch-icon.png"],
      manifest: {
        name: "MyApp",
        short_name: "MyApp",
        description: "MyApp",
        theme_color: "#0f172a",
        background_color: "#0f172a",
        display: "standalone",
        start_url: "/",
        icons: [
          { src: "pwa-192.png", sizes: "192x192", type: "image/png" },
          { src: "pwa-512.png", sizes: "512x512", type: "image/png" },
          { src: "pwa-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
        ],
      },
      workbox: {
        // The service worker answers page navigations with the cached shell.
        // These paths are the server's, not the SPA's: without this, clicking
        // "Sign in with Google" (/api/v1/auth/google/login) would get index.html
        // instead of the redirect to Google.
        navigateFallbackDenylist: [/^\/api\//, /^\/docs/, /^\/openapi\.json/, /^\/health/],
      },
    }),
  ],
  resolve: {
    // `import { api } from "@/lib/api"` instead of "../../../lib/api".
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    host: true, // listen on 0.0.0.0 so the container's port mapping works
    port: 5173,
    proxy: {
      // Proxying (rather than pointing fetch at http://localhost:8000) keeps
      // every request same-origin in dev too, so cookies and CORS behave the
      // same way locally as they do in production.
      "/api": { target: apiTarget, changeOrigin: true, ws: true },
    },
  },
  build: {
    // Fail the build on a TS/asset error rather than shipping a broken bundle
    // that only breaks in the browser.
    sourcemap: true,
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: false,
  },
});

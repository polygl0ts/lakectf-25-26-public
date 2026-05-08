import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    cssCodeSplit: false,
    sourcemap: false,
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
        manualChunks: undefined,
        entryFileNames: "assets/app.js",
        chunkFileNames: "assets/app.js",
        assetFileNames: "assets/[name][extname]"
      }
    }
  }
});

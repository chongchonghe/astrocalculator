import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { equationsPlugin } from './vite-plugin-equations';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    equationsPlugin(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        maximumFileSizeToCacheInBytes: 40 * 1024 * 1024, // Pyodide WASM ~30MB
        globPatterns: ['**/*.{js,css,html,wasm,json,data,png,svg,woff2}'],
      },
      manifest: {
        name: 'AstroCalculator',
        short_name: 'AstroCalc',
        description: 'Calculator for Astronomers and Physicists',
        theme_color: '#1a1a2e',
        icons: [],
      },
    }),
  ],
  base: '/astrocalculator/',
});

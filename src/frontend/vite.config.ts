import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ['host.docker.internal'],
    host: true,
    proxy: {
      '/weather/api': {
        target: process.env.WEATHER_HTTPS || process.env.WEATHER_HTTP,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/weather/, '')
      },
      '/weather-ai-outfit/api': {
        target: process.env.WEATHER_AI_OUTFIT_HTTPS || process.env.WEATHER_AI_OUTFIT_HTTP,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/weather-ai-outfit/, '')
      }
    }
  }
});

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// In dev, /api/* is forwarded to the api so the browser sees one origin (no CORS, cookies just work).
// In production the reverse proxy does the same.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: process.env.API_PROXY ?? 'http://localhost:3100',
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});

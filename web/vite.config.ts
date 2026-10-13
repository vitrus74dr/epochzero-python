import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev: run `uv run epochzero --dev` (API on :8765) and `pnpm dev` (UI on :5173).
// changeOrigin stays false so the backend's Host/Origin guard sees :5173.
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8765', ws: true },
    },
  },
})

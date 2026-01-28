import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // No rewrite as per the "proxy all requests starting with /api" instruction
        // unless specified. But usually /api/v1/... -> /v1/...
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})

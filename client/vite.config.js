import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/upload': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/enhance': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/download-tex': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/download-pdf': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})

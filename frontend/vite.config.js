import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env variables from system and .env files
  const env = loadEnv(mode, process.cwd(), '');
  const backendTarget = env.VITE_BACKEND_URL || 'http://127.0.0.1:5000';

  return {
    plugins: [react()],
    server: {
      port: 5173,
      host: true, // needed for Docker container access
      proxy: {
        '/upload': {
          target: backendTarget,
          changeOrigin: true,
        },
        '/enhance': {
          target: backendTarget,
          changeOrigin: true,
        },
        '/download-tex': {
          target: backendTarget,
          changeOrigin: true,
        },
        '/download-pdf': {
          target: backendTarget,
          changeOrigin: true,
        },
        '/find-jobs': {
          target: backendTarget,
          changeOrigin: true,
        },
      },
    },
  }
})

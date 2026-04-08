import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// All routes that FastAPI owns are proxied from the React dev server (localhost:5173)
// to FastAPI (localhost:8000). This means:
//   - The browser only ever talks to one origin (localhost:5173)
//   - Cookies set by FastAPI are scoped to localhost:5173, so they're sent
//     with every proxied /api request automatically
//   - No CORS errors in development

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api':         { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/login':       { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/logout':      { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/auth':        { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/me':          { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})

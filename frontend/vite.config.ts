import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// The React app calls relative URLs like /api/babies. In development Vite
// forwards those to FastAPI, so the browser sees one origin and no CORS issue.
// Inside docker-compose the API is reachable as http://api:8000.
const apiTarget = process.env.API_PROXY_TARGET ?? 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': apiTarget,
    },
  },
})

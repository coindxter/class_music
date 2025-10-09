import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, 
    proxy: {
      '/classes': 'http://localhost:5050',
      '/classes_full': 'http://localhost:5050',
      '/add_class': 'http://localhost:5050',
      '/add_student': 'http://localhost:5050',
      '/add_artist': 'http://localhost:5050',
      '/add_song': 'http://localhost:5050',
      '/delete': 'http://localhost:5050',
    },
  },
  build: {
    outDir: 'dist',
  },
})

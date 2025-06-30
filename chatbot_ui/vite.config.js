import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  server: {
    port: 9475, // Set development server port
  },
  preview: {
    port: 9475, // Set preview server port for production builds
  },
  plugins: [react()],
})

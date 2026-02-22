import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite' // இந்த வரியைச் சேர்க்கவும்

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(), // இதை இங்கே சேர்க்கவும்
  ],
})
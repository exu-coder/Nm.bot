import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['farabi-admin-nmbot.onrender.com']
  },
  preview: {
    host: '0.0.0.0',
    port: 4173,
    allowedHosts: ['farabi-admin-nmbot.onrender.com']
  },
  build: {
    target: 'es2020'
  }
});

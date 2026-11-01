import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  // Serve shared static files from src/assets without Vite changing their names.
  publicDir: './src/assets',
});

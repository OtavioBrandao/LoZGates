/// <reference types="vitest/config" />
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import react from '@vitejs/plugin-react';
import { defineConfig, type Plugin } from 'vite';

const PASTA_WEB = path.dirname(fileURLToPath(import.meta.url));
// "LoZGates 1.0.1/" — onde ficam assets/ (ícone e fonte Momentz) e o BackEnd
const PASTA_APP = path.resolve(PASTA_WEB, '..');
const ICONE = path.join(PASTA_APP, 'assets', 'icon.ico');

// Onde a API roda durante o desenvolvimento (uvicorn BackEnd.api.app:app)
const API = process.env.LOZGATES_API ?? 'http://127.0.0.1:8000';

/** Usa o mesmo ícone do desktop (assets/icon.ico) sem copiá-lo para dentro de web/. */
function pluginIcone(): Plugin {
  return {
    name: 'lozgates-icone',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if ((req.url || '').split('?')[0].endsWith('/favicon.ico') && fs.existsSync(ICONE)) {
          res.setHeader('Content-Type', 'image/x-icon');
          res.end(fs.readFileSync(ICONE));
          return;
        }
        next();
      });
    },
    generateBundle() {
      if (fs.existsSync(ICONE)) {
        this.emitFile({ type: 'asset', fileName: 'favicon.ico', source: fs.readFileSync(ICONE) });
      }
    },
  };
}

export default defineConfig({
  // Caminhos relativos: o build funciona servido pela API ("/") ou numa subpasta
  base: './',
  plugins: [react(), pluginIcone()],
  server: {
    // A fonte Momentz fica em ../assets
    fs: { allow: [PASTA_APP] },
    proxy: { '/api': API },
  },
  preview: {
    proxy: { '/api': API },
  },
  build: {
    target: 'es2022',
  },
  test: {
    include: ['src/**/*.test.ts'],
    environment: 'node',
  },
});

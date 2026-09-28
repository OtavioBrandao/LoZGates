import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import react from '@vitejs/plugin-react';
import { zipSync } from 'fflate';
import { defineConfig, type Plugin } from 'vite';

const PASTA_WEB = path.dirname(fileURLToPath(import.meta.url));
// "LoZGates 1.0.1/" — onde estão BackEnd/, FrontEnd/, config.py e assets/
const PASTA_APP = path.resolve(PASTA_WEB, '..');
const PASTA_LOZWEB = path.join(PASTA_WEB, 'python', 'lozweb');

const NOME_PACOTE_PYTHON = 'lozgates-python.zip';

function listarPython(pasta: string, prefixo: string, saida: Record<string, Uint8Array>) {
  if (!fs.existsSync(pasta)) return;
  for (const item of fs.readdirSync(pasta, { withFileTypes: true })) {
    if (item.name === '__pycache__' || item.name.startsWith('.')) continue;
    const caminho = path.join(pasta, item.name);
    const nome = `${prefixo}/${item.name}`;
    if (item.isDirectory()) listarPython(caminho, nome, saida);
    else if (item.name.endsWith('.py')) saida[nome] = fs.readFileSync(caminho);
  }
}

/**
 * Empacota o código Python ORIGINAL do LoZ Gates (sem cópias no repositório):
 *   ../BackEnd/**.py, ../FrontEnd/**.py, ../config.py  +  python/lozweb/**.py
 * O navegador baixa esse .zip e o descompacta no sistema de arquivos do Pyodide.
 */
function empacotarPython(): Uint8Array {
  const arquivos: Record<string, Uint8Array> = {};
  listarPython(path.join(PASTA_APP, 'BackEnd'), 'BackEnd', arquivos);
  listarPython(path.join(PASTA_APP, 'FrontEnd'), 'FrontEnd', arquivos);
  listarPython(PASTA_LOZWEB, 'lozweb', arquivos);
  arquivos['config.py'] = fs.readFileSync(path.join(PASTA_APP, 'config.py'));
  // ASSETS_PATH (config.py): onde o desktop grava circuito.png e entrada.txt
  arquivos['assets/.mantida'] = new Uint8Array();
  return zipSync(arquivos, { level: 6 });
}

function pluginLozGates(): Plugin {
  const icone = path.join(PASTA_APP, 'assets', 'icon.ico');
  return {
    name: 'lozgates-python',
    configureServer(server) {
      server.watcher.add([
        path.join(PASTA_APP, 'BackEnd'),
        path.join(PASTA_APP, 'FrontEnd'),
        path.join(PASTA_APP, 'config.py'),
        PASTA_LOZWEB,
      ]);
      server.watcher.on('change', (arquivo) => {
        if (arquivo.endsWith('.py')) server.ws.send({ type: 'full-reload' });
      });
      server.middlewares.use((req, res, next) => {
        const url = (req.url || '').split('?')[0];
        if (url.endsWith(`/${NOME_PACOTE_PYTHON}`)) {
          res.setHeader('Content-Type', 'application/zip');
          res.setHeader('Cache-Control', 'no-store');
          res.end(Buffer.from(empacotarPython()));
          return;
        }
        if (url.endsWith('/favicon.ico') && fs.existsSync(icone)) {
          res.setHeader('Content-Type', 'image/x-icon');
          res.end(fs.readFileSync(icone));
          return;
        }
        next();
      });
    },
    generateBundle() {
      this.emitFile({ type: 'asset', fileName: NOME_PACOTE_PYTHON, source: empacotarPython() });
      if (fs.existsSync(icone)) {
        this.emitFile({ type: 'asset', fileName: 'favicon.ico', source: fs.readFileSync(icone) });
      }
    },
  };
}

export default defineConfig({
  // Caminhos relativos: o build funciona em qualquer subpasta (ex.: GitHub Pages /LoZGates/)
  base: './',
  plugins: [react(), pluginLozGates()],
  server: {
    // Permite usar a fonte Momentz de ../assets
    fs: { allow: [PASTA_APP] },
  },
  build: {
    target: 'es2022',
    chunkSizeWarningLimit: 800,
  },
});

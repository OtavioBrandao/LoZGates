#!/usr/bin/env node
/**
 * Baixa para public/pyodide/ só os arquivos do Pyodide que o LoZ Gates usa
 * (interpretador + biblioteca padrão + pygame-ce + Pillow, ~15 MB), para hospedar tudo
 * junto do site em vez de depender do CDN.
 *
 * Uso:
 *   npm run pyodide:baixar                      # baixa do CDN jsDelivr
 *   npm run pyodide:baixar -- --origem ./dist   # copia de uma distribuição já extraída
 * Depois:
 *   VITE_PYODIDE_URL=./pyodide/ npm run build
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const VERSAO = '0.29.3';
const PACOTES = ['pygame-ce', 'pillow'];
const NUCLEO = ['pyodide.mjs', 'pyodide.js', 'pyodide.asm.js', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json'];

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const destino = path.join(raiz, 'public', 'pyodide');
const argOrigem = process.argv.indexOf('--origem');
const origemLocal = argOrigem > 0 ? path.resolve(process.argv[argOrigem + 1]) : null;
const cdn = process.env.PYODIDE_CDN || `https://cdn.jsdelivr.net/pyodide/v${VERSAO}/full/`;

async function obter(nome) {
  if (origemLocal) return fs.readFileSync(path.join(origemLocal, nome));
  const resposta = await fetch(cdn + nome);
  if (!resposta.ok) throw new Error(`${nome}: HTTP ${resposta.status}`);
  return Buffer.from(await resposta.arrayBuffer());
}

async function salvar(nome) {
  const dados = await obter(nome);
  fs.writeFileSync(path.join(destino, nome), dados);
  console.log(`  ✓ ${nome} (${(dados.length / 1024 / 1024).toFixed(2)} MB)`);
  return dados;
}

fs.mkdirSync(destino, { recursive: true });
console.log(`Pyodide ${VERSAO} → ${path.relative(raiz, destino)}/  (origem: ${origemLocal ?? cdn})`);
for (const nome of NUCLEO) await salvar(nome);

const trava = JSON.parse(fs.readFileSync(path.join(destino, 'pyodide-lock.json'), 'utf8'));
const necessarios = new Set();
const incluir = (nome) => {
  if (necessarios.has(nome)) return;
  const pacote = trava.packages[nome];
  if (!pacote) throw new Error(`Pacote ${nome} não existe no pyodide-lock.json`);
  necessarios.add(nome);
  pacote.depends.forEach(incluir);
};
PACOTES.forEach(incluir);
for (const nome of necessarios) await salvar(trava.packages[nome].file_name);
console.log('Pronto. Gere o site com: VITE_PYODIDE_URL=./pyodide/ npm run build');

/**
 * Teste ponta a ponta do LoZ Gates Web (Chrome/Chromium headless).
 *
 *   npm run build && npm run preview          # em um terminal
 *   CHROME_PATH=/caminho/do/chrome npm run test:e2e
 *
 * Percorre todas as telas: manual, conversão, circuito (pygame → PNG), tabela verdade,
 * simplificação (resultado e interativa), IA, circuito interativo (monta (A*B)+~C com
 * cliques reais no pygame e testa com ESPAÇO), banco de problemas, equivalência,
 * encerramento de sessão com os dados de uso e o layout de celular.
 */
import fs from 'node:fs';
import puppeteer from 'puppeteer-core';

const CHROMES = [
  process.env.CHROME_PATH,
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
];
const executavel = CHROMES.find((c) => c && fs.existsSync(c));
if (!executavel) {
  console.error('Chrome não encontrado. Defina CHROME_PATH=/caminho/do/chrome');
  process.exit(2);
}

const URL_APP = process.env.URL_APP || 'http://localhost:4173/';
const SAIDA = process.argv[2] || './out';
fs.mkdirSync(SAIDA, { recursive: true });

const navegador = await puppeteer.launch({
  executablePath: executavel,
  args: ['--no-sandbox'],
  headless: true,
  defaultViewport: { width: 1366, height: 900 },
});
const pagina = await navegador.newPage();
const logs = [];
const erros = [];
pagina.on('console', (m) => logs.push(m.text()));
pagina.on('pageerror', (e) => erros.push('PAGEERROR ' + e.message));
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
let passo = 0;
const ok = (msg) => console.log(`✔ ${String(++passo).padStart(2, '0')} ${msg}`);
const falha = (msg) => {
  console.log(`✘ ${msg}`);
  process.exitCode = 1;
};
const verificar = (cond, msg) => (cond ? ok(msg) : falha(msg));
const foto = (nome) => pagina.screenshot({ path: `${SAIDA}/${nome}.png` });

async function clicar(texto, { dentro = 'body', indice = 0 } = {}) {
  const alvo = await pagina.evaluateHandle(
    (texto, dentro, indice) => {
      const raiz = document.querySelector(dentro) || document.body;
      const candidatos = [...raiz.querySelectorAll('button')].filter((b) => b.textContent.replace(/\s+/g, ' ').includes(texto) && b.offsetParent !== null);
      return candidatos[indice] || null;
    },
    texto,
    dentro,
    indice,
  );
  const el = alvo.asElement();
  if (!el) throw new Error(`Botão não encontrado: ${texto}`);
  await el.click();
  await esperar(120);
}
const texto = () => pagina.evaluate(() => document.body.innerText);
const temTexto = async (t) => (await texto()).includes(t);
async function esperarTexto(t, ms = 15000) {
  const fim = Date.now() + ms;
  while (Date.now() < fim) {
    if (await temTexto(t)) return true;
    await esperar(100);
  }
  return false;
}
async function digitar(seletor, valor) {
  await pagina.$eval(seletor, (el) => { el.focus(); el.select(); });
  await pagina.keyboard.press('Backspace');
  await pagina.type(seletor, valor);
}
async function fecharModal() {
  await pagina.evaluate(() => {
    const abertos = [...document.querySelectorAll('dialog[open]')];
    abertos.at(-1)?.querySelector('.modal__fechar')?.click();
  });
  await esperar(150);
}
const modaisAbertos = () => pagina.evaluate(() => [...document.querySelectorAll('dialog[open] .modal__titulo')].map((e) => e.textContent));

// ---------------------------------------------------------------------------
const t0 = Date.now();
await pagina.goto(URL_APP);
verificar(await esperarTexto('Circuitos e Expressões', 90000), `carregou o motor Python em ${((Date.now() - t0) / 1000).toFixed(1)}s`);
await esperar(1100);
await foto('01_inicio');

// Ajuda
await clicar('Ajuda');
verificar((await modaisAbertos()).includes('📚 LoZ Gates - manual interativo'), 'abriu o manual interativo');
for (const aba of ['Funcionalidades', 'Sintaxe', 'Exemplos', 'Leis', 'Controles', 'Dicas', 'Créditos']) await clicar(aba, { dentro: 'dialog[open]' });
verificar(await temTexto('Obrigado por usar o LoZ Gates!'), 'percorreu as 8 abas do manual');
await foto('02_manual');
await clicar('Sobre', { dentro: 'dialog[open]' });
await fecharModal();

// Principal
await clicar('Circuitos e Expressões');
verificar(await temTexto('Digite a expressão em Lógica Proposicional:'), 'abriu a tela de expressão');
await clicar('Confirmar');
verificar((await texto()).includes('A expressão não pode estar vazia.'), 'validação de expressão vazia (popup)');
await clicar('OK', { dentro: 'dialog[open]' });
await pagina.type('input[aria-label="Expressão em lógica proposicional"]', '(a & b) | !c');
await pagina.keyboard.press('Enter');
verificar(await esperarTexto('Ver Circuito', 3000), 'Enter confirma e mostra "Ver Circuito"');
await foto('03_principal');
await clicar('Ver Circuito');
verificar(await esperarTexto('Expressão Lógica Proposicional: (A&B)|!C'), 'gerou o circuito e abriu as abas');
const img = await pagina.evaluate(() => {
  const i = document.querySelector('.aba-circuito img');
  return i ? { w: i.naturalWidth, h: i.naturalHeight } : null;
});
verificar(img && img.w === 1220 && img.h === 820, `imagem do circuito (pygame + borda Pillow) ${JSON.stringify(img)}`);
await foto('04_aba_circuito');

// ❓ e salvar
await pagina.click('.botao-duvida');
verificar(await esperarTexto('GUIA RÁPIDO - CIRCUITOS INTERATIVOS', 2000), 'popup de dúvida com texto do config.py');
await fecharModal();
await clicar('Salvar circuito como PNG');
verificar(await temTexto('Imagem salva com sucesso!'), 'salvar PNG');
await clicar('OK', { dentro: 'dialog[open]' });

// Aba Expressão
await clicar('Expressão', { dentro: '[role=tablist]' });
await clicar('Realizar conversão');
verificar(await temTexto('(A*B)+~C'), 'conversão para álgebra booleana');
await clicar('Tabela Verdade');
const tabela = await pagina.evaluate(() => ({
  cols: [...document.querySelectorAll('dialog[open] th')].map((t) => t.textContent),
  linhas: document.querySelectorAll('dialog[open] tbody tr').length,
  conclusao: document.querySelector('.tabela-verdade__conclusao')?.textContent,
}));
verificar(tabela.linhas === 8 && tabela.conclusao === 'A expressão é SATISFATÍVEL.', `tabela verdade ${JSON.stringify(tabela)}`);
await foto('05_tabela_verdade');
await clicar('Fechar', { dentro: 'dialog[open] .modal__rodape' });

// Simplificar - Resultado
await clicar('Simplificar - Resultado');
verificar(await esperarTexto('Progresso da Simplificação', 5000), 'abriu "Solução da expressão"');
verificar(await esperarTexto('Expressão Resultante', 8000), 'StepView concluiu (com o ritmo de 1s por iteração)');
await foto('06_resolucao');
await clicar('Voltar');
verificar(await esperarTexto('Simplificar - Interativo', 3000), 'voltar_para_abas mantém os botões de simplificação');

// Simplificar - Interativo
await clicar('Simplificar - Interativo');
verificar(await esperarTexto('Analisando subexpressão', 5000), 'modo interativo iniciou');
const pulos = () => pagina.evaluate(() => document.querySelectorAll('.lista-passos .cartao-passo--pular').length);
const pulosAntes = await pulos();
await clicar('Pular');
verificar((await pulos()) === pulosAntes + 1, 'pular registra subexpressão ignorada');
await clicar('Desfazer');
verificar((await pulos()) === pulosAntes, 'desfazer remove o último passo');
let aplicou = false;
for (let rodada = 0; rodada < 5 && !aplicou; rodada++) {
  for (let i = 0; i < 9 && !aplicou; i++) {
    const antes = await pagina.evaluate(() => document.querySelectorAll('.lista-passos .cartao-passo--sucesso').length);
    await clicar('', { dentro: '.grade-leis', indice: i });
    if ((await modaisAbertos()).includes('Erro')) await clicar('OK', { dentro: 'dialog[open]' });
    aplicou = (await pagina.evaluate(() => document.querySelectorAll('.lista-passos .cartao-passo--sucesso').length)) > antes;
  }
  if (!aplicou) await clicar('Pular');
}
verificar(aplicou, 'aplicou uma lei com sucesso');
await foto('07_interativo');
await clicar('Sugestão de IA');
verificar((await modaisAbertos()).includes('Sugestão de IA - Simplificador Lógico'), 'abriu o chat de IA');
verificar(await esperarTexto('Erro de conexão', 15000) || await esperarTexto('Erro ao conectar', 100), 'IA sem rede: erro tratado pelo ai_assistant.py original');
await clicar('Explicar Leis', { dentro: 'dialog[open]' });
verificar(await temTexto('Principais leis da lógica proposicional'), 'explicar leis');
await foto('08_chat_ia');
await clicar('Fechar', { dentro: 'dialog[open] .modal__rodape' });
await clicar('Voltar');

// Circuito Interativo
await clicar('Circuito Interativo', { dentro: '[role=tablist]' });
verificar(await esperarTexto('Selecione o Modo de Desafio:', 3000), 'tela de modos do circuito interativo');
await clicar('Iniciar Desafio');
verificar(await temTexto('⚠️ Selecione um modo de desafio primeiro'), 'exige modo antes de iniciar');
await clicar('Portas Básicas');
verificar(await temTexto('Modo selecionado: Portas Básicas | Pronto para iniciar!'), 'selecionou Portas Básicas');
await clicar('Iniciar Desafio');
await esperar(900);
const canvas = await pagina.evaluate(() => {
  const c = document.querySelector('.area-pygame canvas');
  if (!c) return null;
  const r = c.getBoundingClientRect();
  return { w: c.width, h: c.height, x: r.x, y: r.y, cw: r.width, ch: r.height };
});
verificar(canvas && canvas.w >= 800 && canvas.h === 600, `pygame desenhando no canvas ${JSON.stringify(canvas)}`);
await pagina.evaluate(() => document.querySelector('.area-pygame').scrollIntoView({ block: 'center' }));
await esperar(300);
const c2 = await pagina.evaluate(() => {
  const r = document.querySelector('.area-pygame canvas').getBoundingClientRect();
  return { x: r.x, y: r.y };
});
const W = canvas.w,
  H = canvas.h;
const tela = ([wx, wy]) => [Math.round(wx + W / 2), Math.round(wy + H / 2)];
const clicarCanvas = async ([sx, sy]) => {
  await pagina.mouse.move(c2.x + sx, c2.y + sy, { steps: 3 });
  await pagina.mouse.down();
  await esperar(50);
  await pagina.mouse.up();
  await esperar(90);
};
// variáveis: (-300, -100 + i*100) 80x60 -> saída (x+80, y+30); saída do circuito em (300,0) -> entrada (300, 30)
const saidaVar = (i) => [-300 + 80, -100 + i * 100 + 30];
const paleta = (i) => [70, 200 + 30 + i * 50 + 22];
async function colocar(indicePaleta, [sx, sy]) {
  await clicarCanvas(paleta(indicePaleta));
  await pagina.mouse.move(c2.x + sx, c2.y + sy, { steps: 4 });
  await esperar(80);
  await clicarCanvas([sx, sy]);
  const [wx, wy] = [sx - W / 2 - 40, sy - H / 2 - 30];
  return { x: wx, y: wy };
}
const e = await colocar(0, tela([-100, -100])); // AND
const n = await colocar(2, tela([-100, 150])); // NOT
const o = await colocar(1, tela([100, 30])); // OR
const entradas2 = (g) => [
  [g.x, g.y + 40 - 20],
  [g.x, g.y + 40 + 20],
];
await clicarCanvas(tela(saidaVar(0)));
await clicarCanvas(tela(entradas2(e)[0]));
await clicarCanvas(tela(saidaVar(1)));
await clicarCanvas(tela(entradas2(e)[1]));
await clicarCanvas(tela(saidaVar(2)));
await clicarCanvas(tela([n.x, n.y + 40]));
await clicarCanvas(tela([e.x + 40, e.y + 40]));
await clicarCanvas(tela(entradas2(o)[0]));
await clicarCanvas(tela([n.x + 46, n.y + 40]));
await clicarCanvas(tela(entradas2(o)[1]));
await clicarCanvas(tela([o.x + 40, o.y + 40]));
await clicarCanvas(tela([300, 30]));
const conexoes = logs.filter((l) => l.startsWith('✅ Conexão criada')).length;
verificar(conexoes === 6, `6 fios conectados no pygame (${conexoes})`);
await pagina.keyboard.press('Space');
await esperar(300);
verificar(logs.some((l) => l.includes('✅ Circuito correto!')), 'ESPAÇO testa o circuito: "✅ Circuito correto!"');
await foto('09_circuito_interativo_sucesso');
await pagina.mouse.move(c2.x + W / 2, c2.y + H / 2);
await pagina.mouse.wheel({ deltaY: -200 });
await esperar(200);
const rolagem = await pagina.evaluate(() => window.scrollY);
await pagina.mouse.wheel({ deltaY: -200 });
await esperar(200);
verificar((await pagina.evaluate(() => window.scrollY)) === rolagem, 'rodinha sobre o pygame dá zoom sem rolar a página');
await clicar('Resetar vista');
await clicar('Controles', { dentro: '.seletor-circuito__controles' });
verificar(await temTexto('CONTROLES BÁSICOS'), 'painel de controles');
await clicar('Dicas', { dentro: '.seletor-circuito__controles' });
verificar(await temTexto('💡 DICAS - Portas Básicas (Iniciante)'), 'painel de dicas do modo');
await clicar('Desafio NAND');
verificar(await temTexto('⚠️ Pare o circuito antes de trocar de modo') || (await pagina.evaluate(() => [...document.querySelectorAll('.botao-modo')].filter((b) => b.disabled).length)) === 5, 'modos bloqueados com circuito ativo');
await clicar('Parar');
verificar(await temTexto('⏹️ Circuito parado - Selecione um modo para reiniciar'), 'parar circuito');
await esperar(200);
verificar(logs.some((l) => l.includes('🛑 Circuito interativo parado')), 'CircuitoInterativoManual.stop() chamado');

// voltar para principal limpa a entrada
await clicar('Voltar', { dentro: 'main:not([hidden]) .topo-tela' });
const entradaAposVoltar = await pagina.$eval('input[aria-label="Expressão em lógica proposicional"]', (i) => i.value);
verificar(entradaAposVoltar === '', 'go_back_to(principal) limpa a entrada');

// Banco de problemas
await clicar('Banco de problemas');
const nProblemas = await pagina.evaluate(() => document.querySelectorAll('.botao-problema').length);
verificar(nProblemas === 32, `lista de problemas (${nProblemas})`);
await foto('10_problemas');
await clicar('Airbags');
verificar(await temTexto('📖 Problema:'), 'abriu problema Airbags');
await clicar('Verificar Resposta');
verificar(await temTexto('⚠️ Por favor, digite uma resposta'), 'resposta vazia');
await pagina.type('input[aria-label="Sua resposta"]', 'V & P');
await clicar('Verificar Resposta');
verificar(await temTexto('❌ Resposta incorreta'), 'resposta incorreta');
await clicar('Mostrar Resposta');
verificar(await temTexto('💡 Resposta Correta:'), 'mostrar resposta liberado após tentativa');
await digitar('input[aria-label="Sua resposta"]', 'I & (P & V)');
await clicar('Verificar Resposta');
verificar(await temTexto('✅ Resposta correta! Parabéns!'), 'resposta equivalente aceita');
await foto('11_problema');
await clicar('Tabela Verdade');
verificar((await modaisAbertos()).includes('Tabela Verdade'), 'analisar na tabela verdade');
await fecharModal();
await clicar('Banco de problemas');
await clicar('Airbags');
await pagina.type('input[aria-label="Sua resposta"]', 'V&P&I');
await clicar('Verificar Resposta');
await clicar('Analisar no Circuito');
verificar(await esperarTexto('Expressão Lógica Proposicional: V&P&I', 5000), 'analisar no circuito (handle_problem_answer)');
await clicar('Voltar', { dentro: 'main:not([hidden]) .topo-tela' });
await clicar('Voltar', { dentro: 'main .topo-tela' });

// Equivalência
await clicar('Equivalência Lógica');
await pagina.type('input[aria-label="Primeira expressão"]', 'A>B');
await pagina.type('input[aria-label="Segunda expressão"]', '!A|B');
await clicar('Comparar');
verificar(await temTexto('✅ São equivalentes!'), 'A>B ≡ !A|B');
await digitar('input[aria-label="Segunda expressão"]', 'A|B');
await clicar('Comparar');
verificar(await temTexto('❌ Não são equivalentes'), 'A>B ≢ A|B');
await foto('12_equivalencia');
await clicar('Voltar');

// Encerrar sessão
await clicar('Encerrar sessão');
verificar((await modaisAbertos()).includes('Compartilhamento de dados detalhados - LoZ Gates Beta'), 'diálogo de compartilhamento (on_closing)');
verificar(await temTexto('RESUMO GERAL'), 'preview gerado por DetailedDataSharingDialog._create_data_preview');
await foto('13_compartilhar');
await clicar('Não Agora');
verificar(await esperarTexto('Sessão encerrada', 2000), 'sessão encerrada');
const guardado = await pagina.evaluate(() => {
  const d = JSON.parse(localStorage.getItem('lozgates:arquivo:user_activity_detailed.json') || '{}');
  return { sessoes: d.sessions?.length, eventos: d.sessions?.at(-1)?.events_count };
});
verificar(guardado.sessoes === 1 && guardado.eventos > 20, `log de uso persistido no navegador ${JSON.stringify(guardado)}`);
await pagina.reload();
await esperarTexto('Circuitos e Expressões', 60000);
await pagina.evaluate(() => {
  [...document.querySelectorAll('button')].find((b) => b.textContent.includes('Encerrar sessão')).click();
});
await esperar(400);
verificar(await temTexto('Total de sessões: 2'), 'sessões anteriores restauradas após recarregar');

// ---------------- Celular (390x844) ----------------
await pagina.setViewport({ width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
await pagina.reload();
await esperarTexto('Circuitos e Expressões', 60000);
await esperar(1000);
const semRolagemLateral = async (nome) => {
  const r = await pagina.evaluate(() => ({ sw: document.documentElement.scrollWidth, w: window.innerWidth }));
  verificar(r.sw <= r.w, `celular sem rolagem lateral: ${nome} (${r.sw}/${r.w})`);
};
await foto('m01_inicio');
await semRolagemLateral('início');
await clicar('Ajuda');
await clicar('Leis', { dentro: 'dialog[open]' });
await foto('m02_manual');
await fecharModal();
await clicar('Circuitos e Expressões');
await pagina.type('input[aria-label="Expressão em lógica proposicional"]', '(A|B)&!(A&B)');
await clicar('Confirmar');
await clicar('Ver Circuito');
await esperarTexto('Expressão Lógica Proposicional:', 5000);
await foto('m03_abas');
await semRolagemLateral('abas/circuito');
await clicar('Circuito Interativo', { dentro: '[role=tablist]' });
await clicar('Modo Livre');
await clicar('Iniciar Desafio');
await esperar(900);
await pagina.evaluate(() => document.querySelector('.area-pygame').scrollIntoView({ block: 'center' }));
await esperar(300);
await foto('m04_circuito_interativo');
await semRolagemLateral('circuito interativo');
const toque = await pagina.evaluate(() => {
  const c = document.querySelector('.area-pygame canvas');
  const r = c.getBoundingClientRect();
  return { x: r.x, y: r.y, escala: r.width / c.width };
});
// toca no botão AND da paleta (coordenadas do pygame escaladas para o tamanho do celular)
await pagina.touchscreen.tap(toque.x + 70 * toque.escala, toque.y + 252 * toque.escala);
await esperar(200);
verificar(logs.some((l) => l.includes('Modo colocação ativado: and')), `toque no celular chega ao pygame (escala ${toque.escala.toFixed(2)})`);
await clicar('Cancelar');
await clicar('Expressão', { dentro: '[role=tablist]' });
await clicar('Realizar conversão');
await clicar('Simplificar - Interativo');
await esperarTexto('Analisando subexpressão', 5000);
await foto('m05_interativo');
await semRolagemLateral('simplificação interativa');
await clicar('Voltar');
await clicar('Tabela Verdade');
await foto('m06_tabela');
await fecharModal();

console.log('\nErros de página:', erros.length ? erros : 'nenhum');
const avisos = logs.filter((l) => /Traceback|Exception in|Error/.test(l) && !/Erro de conexão|Failed to fetch|ERR_|net::/.test(l));
console.log('Exceções Python/JS no console:', avisos.length ? avisos.slice(0, 10) : 'nenhuma');
await navegador.close();

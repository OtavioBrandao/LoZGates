# LoZ Gates Web (versão 1.0.1 no navegador)

Interface nova em **React + TypeScript + Vite**, rodando o **mesmo código Python** do LoZ Gates 1.0.1 dentro do navegador via **[Pyodide](https://pyodide.org)** (CPython compilado para WebAssembly). O circuito interativo em **pygame** roda sem alterações, desenhando num `<canvas>`.

> Nenhum arquivo de `BackEnd/`, `FrontEnd/`, `config.py` ou `main.py` foi modificado. A versão desktop continua funcionando exatamente como antes (`python main.py`).

## Como rodar

Pré‑requisito: Node.js 20 ou mais novo.

```bash
cd "LoZGates 1.0.1/web"
npm install
npm run dev          # abre em http://localhost:5173
```

Alterações em qualquer `.py` (BackEnd, FrontEnd, config ou `python/lozweb`) recarregam a página automaticamente.

### Gerar o site (para publicar)

```bash
npm run build        # gera a pasta dist/
npm run preview      # testa o build em http://localhost:4173
```

A pasta `dist/` é um site estático: funciona em GitHub Pages, Netlify, Vercel, servidor da UFAL, etc. Os caminhos são relativos, então pode ficar em qualquer subpasta (ex.: `https://usuario.github.io/LoZGates/`).

Na primeira visita o navegador baixa ~15 MB (interpretador Python, pygame‑ce e Pillow); depois fica em cache.

### Hospedar o Pyodide junto (sem depender do CDN)

Por padrão o Pyodide vem do CDN jsDelivr. Para laboratórios com internet restrita ou uso offline:

```bash
npm run pyodide:baixar                       # baixa só os arquivos necessários para public/pyodide/
VITE_PYODIDE_URL=./pyodide/ npm run build
```

### Assistente de IA (opcional)

O `BackEnd/ai_assistant.py` original usa o cabeçalho `Authorization: Bearer COLAR CHAVE API`. Para usar uma chave real sem editar o código Python:

```bash
VITE_GROQ_API_KEY=gsk_... npm run build
```

⚠️ Num site estático a chave fica visível para quem abrir o código da página. Para uso público, o ideal é um pequeno proxy no servidor (o TODO.md já cita “ver como colocar a API pra fase de testes”).

## Como funciona

```
┌──────────────────────────── navegador ─────────────────────────────┐
│  React (src/)                                                       │
│    telas, abas, janelas, tabela verdade, chat de IA...              │
│        │ chamar('trocar_para_abas', expressão)          ▲ JSON      │
│        ▼                                                │           │
│  Pyodide (CPython 3.13 em WebAssembly)                              │
│    python/lozweb/api.py  ── chama ──►  BackEnd/*  FrontEnd/*        │
│                                        (arquivos ORIGINAIS)         │
│    pygame-ce ──► <canvas>  (CircuitoInterativoManual sem alteração) │
└─────────────────────────────────────────────────────────────────────┘
```

- **O código Python vem do repositório.** O plugin em `vite.config.ts` empacota `../BackEnd`, `../FrontEnd`, `../config.py` e `python/lozweb` num `.zip` que o navegador descompacta. Não existe cópia dos arquivos: o que está no Git é o que roda.
- **`python/lozweb/`** é a única camada nova em Python, e não contém lógica do LoZ Gates. Ela fornece ao código original o que o desktop fornecia:
  - `tkweb.py` — um objeto com a mesma interface do `tk.Frame` que o pygame usava (`after`, `bind`, `winfo_width`, `focus_set`…). Como o laço do circuito já era `frame.after(16, self._tick)`, ele roda igual no navegador;
  - `plataforma.py` — módulos `tkinter`/`customtkinter` inertes (os arquivos originais os importam) e a troca do driver de vídeo `windows` (forçado em `interactive_circuit.py`) pelo `emscripten`;
  - `rede.py` — `requests.post` feito pelo `fetch()` do navegador, em duas fases, para o `ai_assistant.py` e o envio ao Google Forms rodarem sem alteração;
  - `passos.py` — “Simplificar - Resultado” usando o `StepParser` original; o `time.sleep(1)` entre iterações vira um relógio virtual e a tela revela os passos no mesmo ritmo, sem travar o navegador;
  - `interativo.py` — a lógica do “Simplificar - Interativo”, que no desktop fica dentro de funções aninhadas de `interface.py` (não importáveis), transcrita linha a linha;
  - `api.py` — uma função para cada ação da tela, com as mesmas mensagens e registros do `DetailedUserLogger`.

## O que mudou para quem usa

Tudo o que funcionava no desktop funciona na web, com os mesmos textos. Diferenças inevitáveis do navegador e pequenos acréscimos:

| Desktop | Web |
| --- | --- |
| Ao fechar a janela aparece o diálogo de compartilhamento de dados | O navegador não permite diálogos ao fechar a aba. O botão **Encerrar sessão** (tela inicial) faz o mesmo fluxo; se a aba for fechada direto, a sessão é salva sem o diálogo |
| `user_activity_detailed.json` e `logging_settings.json` na pasta do programa | Os mesmos arquivos, guardados no navegador (localStorage), um conjunto por navegador |
| “Salvar circuito como PNG” abre uma janela de salvar | O PNG vai para a pasta de downloads |
| Circuito interativo só pelo teclado | Mesmo teclado, mais botões de atalho sob o circuito (Testar, Desfazer, Refazer, Remover, Cancelar, Resetar vista) que enviam as mesmas teclas — úteis em tablets |
| Janela com tamanho mínimo 1280×720 | Layout fluido de celulares a monitores ultrawide |
| Ao voltar às abas com outra expressão, a aba “Circuito Interativo” podia mostrar a tela de modos da expressão anterior até se trocar de aba | A tela de modos é recriada para a expressão atual sempre que a aba é aberta |

Comportamentos do desktop foram mantidos de propósito, inclusive os listados no TODO.md (ex.: as inconsistências de Desfazer na simplificação interativa). Corrigi‑los é mudança de lógica e deve ser feito nos arquivos originais — a web acompanha automaticamente.

## Testes

```bash
# Ponta a ponta no Chrome (com `npm run preview` rodando em outro terminal)
CHROME_PATH=/caminho/do/chrome npm run test:e2e

# Paridade desktop × web: executa o FrontEnd/interface.py ORIGINAL (CustomTkinter),
# aperta os mesmos botões nas duas versões e compara o que aparece na tela.
# Precisa de customtkinter, pygame, Pillow e numpy; no Linux sem monitor usa xvfb-run.
npm run test:paridade
```

Resultado na entrega:
- **E2E**: 55 verificações — manual (8 abas), conversão, circuito gerado pelo pygame, tabela verdade, simplificação resultado e interativa, chat de IA, circuito interativo montado com cliques reais no canvas e validado com ESPAÇO (“✅ Circuito correto!”), banco de problemas, equivalência, encerramento de sessão com dados de uso, layout de celular sem rolagem lateral e toque chegando ao pygame.
- **Paridade**: 203 cliques no modo interativo em 4 expressões e 6 expressões no modo resultado — **0 diferenças** entre desktop e web.

## Estrutura

```
web/
├── index.html
├── vite.config.ts           # empacota o Python original no build
├── python/lozweb/           # ponte Python ↔ navegador (sem lógica do LoZ Gates)
├── scripts/baixar-pyodide.mjs
├── src/
│   ├── motor/               # Pyodide, canvas do pygame, rede, persistência
│   ├── estado/              # navegação (equivale ao interface.py) e janelas
│   ├── telas/               # Início, Principal, Abas, Resolução, Interativo, Problemas...
│   ├── modais/              # Tabela verdade, Manual, Chat IA, Compartilhar dados
│   ├── dados/               # conteúdo do manual e botões das leis
│   └── estilos/global.css   # tokens do FrontEnd/design_tokens.py
└── testes/                  # e2e.mjs e paridade/
```

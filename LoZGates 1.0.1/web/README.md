# LoZ Gates Web — interface

Interface em **React + TypeScript + Vite**. Toda a lógica (parser, conversão,
tabela-verdade, simplificações, equivalência, layout e correção dos circuitos,
banco de problemas, resumo do registro de uso e proxy da IA) roda em Python,
na API FastAPI de `BackEnd/api`. A interface só desenha e conversa com ela por
HTTP (`api/...`).

## Como rodar em desenvolvimento

Pré-requisitos: Python 3.10+ com as dependências do projeto e Node.js 18 ou 20+.

```bash
# terminal 1 — API (na pasta "LoZGates 1.0.1")
python -m uvicorn BackEnd.api.app:app --reload --port 8000

# terminal 2 — interface
cd web
npm install
npm run dev        # http://localhost:5173 (o Vite repassa /api para a porta 8000)
```

Para apontar o Vite para outra API: `LOZGATES_API=http://servidor:8000 npm run dev`.

## Build

```bash
npm run build      # gera dist/; a API serve essa pasta na raiz quando ela existe
npm run typecheck
npm test           # testes do editor de circuito (Vitest)
```

## Estrutura

```
web/
├── index.html
├── vite.config.ts            # proxy /api, ícone de ../assets e configuração do Vitest
└── src/
    ├── api/                  # cliente HTTP e formatos das respostas da API
    ├── estado/               # navegação e janelas (equivalem a expression_screen.py e loz_app.py)
    ├── telas/                # Início, Principal, Abas, Resolução, Interativo, Problemas, Equivalência
    ├── circuito/             # circuito em SVG, exportação PNG e o editor interativo
    │   └── editor/           # modelo.ts (regras do editor) + Editor.tsx (desenho e eventos)
    ├── modais/               # tabela verdade, manual, chat de IA, consentimento de dados
    ├── telemetria/           # registro de uso guardado no navegador
    ├── dados/                # conteúdo do manual e botões das leis
    └── estilos/global.css
```

## O que mudou em relação ao desktop

- **Circuito gerado:** o servidor devolve o layout em JSON (mesmas coordenadas
  do desenho pygame) e a interface desenha em SVG. "Salvar circuito como PNG"
  gera a imagem no navegador.
- **Circuito interativo:** o editor foi reescrito em TypeScript com as regras do
  `interactive_circuit.py` (pinos, raio de clique de 15, colisão, espiral,
  arrasto, paleta, teclado). A correção (ESPAÇO) é feita no servidor. Os
  cenários de `src/circuito/editor/paridade-editor.json` são gerados pelo
  código pygame original (`python -m tests.paridade.editor_circuito`) e o
  Vitest confere o editor contra eles. Desfazer/refazer guardam o circuito
  inteiro (no desktop, desfazer uma inclusão não removia a porta).
- **Registro de uso:** o navegador anota as mesmas chamadas do
  `DetailedUserLogger` (sessão no `sessionStorage`, configurações no
  `localStorage`). O botão **Encerrar sessão** da tela inicial faz o que o
  desktop fazia ao fechar a janela: o servidor monta a prévia, o aluno decide
  e só então os dados vão para o Google Forms. "Nunca Perguntar" desliga o
  registro e o diálogo deixa de aparecer.
- **IA:** a chave fica no servidor (`LOZGATES_AI_API_KEY` ou `GROQ_API_KEY`).

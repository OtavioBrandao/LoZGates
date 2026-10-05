# LoZ Gates 1.0.1 — versão web

LoZ Gates é uma ferramenta educacional de lógica proposicional, álgebra
booleana e circuitos digitais (Instituto de Computação da UFAL). Ela converte
expressões, gera tabelas-verdade, compara equivalências, simplifica passo a
passo (automático e interativo), desenha o circuito da expressão, permite
montar circuitos com portas lógicas e traz um banco de problemas do mundo real.
Um assistente de IA opcional explica os passos.

Esta branch (`web-unificado`) é a versão web: a lógica do `interface_update`
em Python, exposta por uma API FastAPI, e a interface em React. O desktop em
CustomTkinter/pygame continua nas branches `main` e `interface_update`.

## Arquitetura

```text
┌───────────────────────────── navegador ─────────────────────────────┐
│ frontend/ (React + TypeScript + Vite)                               │
│ telas, circuito em SVG, editor de circuito, registro de uso local   │
└───────────────┬─────────────────────────────────────────────────────┘
                │ HTTP JSON  /api/...
┌───────────────▼─────────────────────────────────────────────────────┐
│ BackEnd/api (FastAPI) — camada fina: valida, chama o core, devolve  │
│ JSON; também serve frontend/dist                                    │
└───────────────┬─────────────────────────────────────────────────────┘
                │ chamadas Python
┌───────────────▼─────────────────────────────────────────────────────┐
│ BackEnd/core/expression_ast.py — o ÚNICO parser                     │
│ conversão, tabela-verdade, equivalência, simplificações,            │
│ circuito_logico/logic (layout, validação, componentes), problemas,  │
│ telemetria (resumo e envio ao Google Forms), cliente da IA          │
└───────────────┬─────────────────────────────────────────────────────┘
                │ HTTP (opcional)
        serviço de IA (services/, Docker) ──► API compatível com OpenAI/Groq
```

Nada fica guardado no servidor entre requisições: a simplificação interativa
viaja como estado JSON e o registro de uso fica no navegador até o aluno
consentir com o envio.

## Estrutura

```text
LoZGates 1.0.1/
├── BackEnd/
│   ├── core/               # expression_ast.py (parser canônico) e sessao_interativa.py
│   ├── api/                # FastAPI: app.py, rotas/, esquemas.py, erros.py, limites.py
│   ├── circuito_logico/    # logic/ (parser, layout, validação, componentes) e modos.py
│   ├── telemetria/         # registro de uso, reconstrução da sessão e Google Forms
│   └── *.py                # converter, tabela, equivalencia, normalizer, identificar_lei,
│                           # simplificador_interativo, problemas, problems_bank, ai_*
├── frontend/               # interface React (ver frontend/README.md)
├── services/               # serviço HTTP opcional da IA (Docker)
├── tests/                  # pytest: núcleo, consumidores, API e paridade com o interface_update
├── docs/                   # auditoria do merge e relatórios
├── config.py               # caminhos, .env e configuração da IA
└── main.py                 # inicia o servidor e abre o navegador
```

## Requisitos

- Python 3.10 ou mais recente;
- Node.js 18 ou 20+ (só para gerar ou desenvolver a interface);
- opcional: uma chave Groq/OpenAI-compatible para o assistente de IA;
- opcional: Docker com Compose v2, para o serviço de IA separado.

## Como rodar

Na pasta `LoZGates 1.0.1`:

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1   |   Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
python main.py              # http://127.0.0.1:8000 (abre o navegador)
```

`python main.py --porta 8080`, `--host 0.0.0.0` (para acessar pela rede) e
`--sem-navegador` mudam o padrão.

### Desenvolvimento (com recarga automática)

```bash
# terminal 1 — API
python -m uvicorn BackEnd.api.app:app --reload --port 8000

# terminal 2 — interface
cd frontend
npm run dev                 # http://localhost:5173 (repassa /api para a porta 8000)
```

A documentação interativa da API fica em `http://127.0.0.1:8000/api/docs`.

## Testes

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests -q

cd frontend
npm test                    # editor do circuito (Vitest)
npm run typecheck
```

`tests/paridade/` compara a versão nova com uma cópia congelada da lógica do
`interface_update` (o "oráculo"); só as diferenças listadas em
`tests/paridade/diferencas_aprovadas.py` são aceitas. Esses testes usam pygame
e CustomTkinter (por isso estão em `requirements-dev.txt`); sem eles, os
testes que dependem do desenho original são pulados. No PowerShell, para o
pygame não abrir janela: `$env:SDL_VIDEODRIVER='dummy'`.

## Configuração

Copie `.env.example` para `.env` (o `.env` é ignorado pelo Git). Variáveis já
definidas no processo têm prioridade.

| Variável | Padrão | Responsabilidade |
| --- | --- | --- |
| `LOZGATES_DATA_DIR` | `data` | dados locais gravados em execução |
| `LOZGATES_LOG_DIR` | `logs` | arquivos de diagnóstico |
| `LOZGATES_LOG_LEVEL` | `INFO` | nível do console e do log geral |
| `LOZGATES_LOG_MAX_BYTES` | `2000000` | tamanho antes da rotação |
| `LOZGATES_LOG_BACKUP_COUNT` | `5` | arquivos antigos preservados |
| `LOZGATES_AI_API_KEY` | vazio | chave da IA (fica só no servidor) |
| `GROQ_API_KEY` | vazio | nome alternativo da chave |
| `LOZGATES_AI_API_URL` | endpoint Groq | endpoint OpenAI-compatible |
| `LOZGATES_AI_MODEL` | `openai/gpt-oss-120b` | modelo solicitado |
| `LOZGATES_AI_TIMEOUT` | `15` | timeout HTTP, em segundos |
| `LOZGATES_AI_SERVICE_URL` | vazio | usa o serviço de IA em Docker, ex.: `http://127.0.0.1:8001` |
| `LOZGATES_CORS_ORIGINS` | vazio | origens extras liberadas para a API (separadas por vírgula) |

## Serviço de IA em Docker (opcional)

```bash
docker compose up --build -d ai-service
```

O `compose.yaml` publica o serviço na porta 8000, a mesma padrão do LoZ Gates:
troque o mapeamento para `"8001:8000"` e use
`LOZGATES_AI_SERVICE_URL=http://127.0.0.1:8001`, ou rode o LoZ Gates com
`python main.py --porta 8080`. Sem o serviço, basta definir a chave no `.env`.
Health check: `GET /health`.

## Registro de uso e privacidade

O navegador anota as mesmas ações que o desktop registrava (expressões,
leis aplicadas, testes de circuito…), na `sessionStorage` da aba; o
identificador anônimo e a preferência "Nunca Perguntar" ficam no
`localStorage`. Em **Encerrar sessão** (tela inicial) o servidor monta a
prévia e o aluno escolhe enviar, não agora ou nunca. Nada é enviado ao Google
Forms sem esse consentimento, e o servidor não grava as sessões.

## Logs

Diagnóstico em JSON Lines: `logs/lozgates.log` (geral) e `logs/errors.log`
(só erros, com stack trace), com rotação.

## Problemas comuns

- `ModuleNotFoundError`: ative o ambiente virtual e reinstale `requirements.txt`.
- O navegador mostra só `{"detail":"Not Found"}`: a interface não foi gerada;
  rode `npm install` e `npm run build` em `frontend/`.
- `npm run dev` reclama da versão do Node: use Node 18 ou 20+.
- A IA responde que não está configurada: defina a chave (ou a URL do serviço)
  e reinicie o servidor.
- HTTP 401/403/429 na IA: verifique chave, acesso ao modelo e limites; veja
  `logs/errors.log` (a chave nunca é registrada).

O histórico da reconstrução está em `docs/`: diagnóstico inicial, relatório
final do desktop e a auditoria deste merge (`docs/auditoria-merge.md`).

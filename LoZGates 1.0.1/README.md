# LozGates 1.0.1

LozGates é uma aplicação desktop educacional para lógica proposicional e
circuitos digitais. Ela converte expressões, gera tabelas-verdade, compara
equivalências, oferece simplificação direta e interativa, renderiza circuitos e
permite construir circuitos com Pygame. Um assistente de IA opcional pode
explicar os passos sem ser necessário para o restante da aplicação.

## Arquitetura

```text
┌────────────────────────────────────────────────────────────┐
│ Desktop (CustomTkinter/Tkinter)                            │
│ navegação, problemas, tabela, simplificador e chat         │
└──────────────┬────────────────────┬────────────────────────┘
               │ chamadas Python    │ frame embutido
               ▼                    ▼
┌──────────────────────────┐  ┌──────────────────────────────┐
│ Núcleo lógico local      │  │ Pygame                      │
│ conversão, equivalência, │  │ circuito estático/interativo│
│ tabela e simplificação   │  │ câmera e renderização       │
└──────────────────────────┘  └──────────────────────────────┘
               ▲
               │ contrato Python
┌──────────────┴───────────┐       HTTP opcional       ┌─────────────────┐
│ Cliente de IA resiliente├───────────────────────────►│ Serviço IA      │
│ (no desktop)            │                            │ em Docker       │
└─────────────────────────┘                            └────────┬────────┘
                                                              │ HTTPS
                                                              ▼
                                                        API compatível
                                                        com OpenAI/Groq
```

O processamento lógico e o simplificador permanecem módulos locais: são
determinísticos, rápidos e usados diretamente pela interface. Separá-los em
serviços acrescentaria falhas de rede sem benefício prático. A IA é o único
serviço opcional porque tem configuração secreta, latência e indisponibilidade
independentes.

Diretórios principais:

- `FrontEnd/`: interface, componentes visuais, responsividade, ajuda e atividade;
- `BackEnd/`: lógica, simplificação, circuitos Pygame, IA e logging;
- `services/`: serviço HTTP opcional da IA;
- `tests/`: regressões do núcleo, simplificador, IA, layout e Pygame;
- `data/`: arquivos gerados em execução, ignorados pelo Git;
- `logs/`: diagnóstico persistente e rotativo, ignorado pelo Git;
- `docs/`: diagnóstico inicial e relatório da reconstrução.

## Requisitos

- Python 3.10 ou mais recente (validado neste trabalho com 3.12 e 3.13);
- Tk 8.6/Tkinter disponível no sistema;
- dependências de `requirements.txt`;
- Docker Engine com o plugin Compose v2, somente para o serviço opcional;
- uma chave Groq, somente para utilizar o assistente de IA.

As dependências Python possuem faixas compatíveis, em vez de versões sem
limite. `requirements-dev.txt` acrescenta apenas o PyInstaller.

## Instalação no Windows

No PowerShell, a partir deste diretório:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python main.py
```

Se a política do PowerShell impedir a ativação, é possível executar diretamente:

```powershell
.\.venv\Scripts\python.exe main.py
```

## Instalação no Linux

Em distribuições Debian/Ubuntu, instale primeiro Python, venv e Tk:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-tk
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python main.py
```

O driver SDL não é mais fixado em `windows`. Em X11 ele usa `x11`; em Wayland
deixa o SDL escolher o backend disponível. O desktop requer uma sessão gráfica.

## Configuração

Copie `.env.example` para `.env`. O carregador local não sobrescreve variáveis
já definidas no processo, portanto variáveis do shell têm prioridade. `.env` é
ignorado pelo Git e nunca deve ser versionado.

| Variável | Padrão | Responsabilidade |
| --- | --- | --- |
| `LOZGATES_DATA_DIR` | `data` | JSON, cache de entrada e PNG gerado |
| `LOZGATES_LOG_DIR` | `logs` | arquivos de diagnóstico |
| `LOZGATES_LOG_LEVEL` | `INFO` | nível do console e do log geral |
| `LOZGATES_LOG_MAX_BYTES` | `2000000` | tamanho antes da rotação |
| `LOZGATES_LOG_BACKUP_COUNT` | `5` | arquivos antigos preservados |
| `LOZGATES_AI_API_KEY` | vazio | chave principal da IA |
| `GROQ_API_KEY` | vazio | nome alternativo da chave |
| `LOZGATES_AI_API_URL` | endpoint Groq | endpoint OpenAI-compatible |
| `LOZGATES_AI_MODEL` | `openai/gpt-oss-120b` | modelo solicitado |
| `LOZGATES_AI_TIMEOUT` | `15` | timeout HTTP, em segundos |
| `LOZGATES_AI_SERVICE_URL` | vazio | proxy local, por exemplo `http://127.0.0.1:8000` |
| `LOZGATES_AI_SERVICE_HOST` | `0.0.0.0` | bind do serviço Docker |
| `LOZGATES_AI_SERVICE_PORT` | `8000` | porta do serviço Docker |

## Execução

Com o ambiente virtual ativo:

```bash
python main.py
```

O entry point prepara diretórios, inicializa o logging e só então carrega a
interface. Para gerar um executável local:

```bash
python -m pip install -r requirements-dev.txt
pyinstaller front.spec
```

## Serviço de IA e Docker

A interface gráfica e o Pygame continuam no host. Apenas o boundary de IA é
containerizado.

1. Defina `GROQ_API_KEY` ou `LOZGATES_AI_API_KEY` no `.env`.
2. Inicie o serviço:

```bash
docker compose up --build -d ai-service
docker compose ps
docker compose logs -f ai-service
```

3. No processo desktop, configure:

```text
LOZGATES_AI_SERVICE_URL=http://127.0.0.1:8000
```

4. Para parar ou reconstruir:

```bash
docker compose down
docker compose build --no-cache ai-service
docker compose up -d ai-service
```

O health check está em `GET /health`. O contrato consumido pelo desktop é
`POST /v1/chat/completions`, com `messages`, `max_tokens` e `temperature`; a
resposta bem-sucedida contém `content`.

## IA sem Docker

Para acesso direto, deixe `LOZGATES_AI_SERVICE_URL` vazio e defina uma chave:

```text
LOZGATES_AI_API_KEY=sua-chave-local
```

Nenhuma chave está hardcoded. A requisição ocorre em uma thread e o resultado
volta ao event loop do Tkinter. Ausência de chave, timeout, erro HTTP, resposta
inválida e indisponibilidade aparecem como mensagem compreensível no chat e são
registrados; o restante do LozGates continua funcional.

## Logs e dados locais

Diagnóstico estruturado em JSON Lines:

- `logs/lozgates.log`: eventos a partir do nível configurado;
- `logs/errors.log`: somente `ERROR`/`CRITICAL`, incluindo stack trace;
- backups rotativos: `lozgates.log.1`, `errors.log.1` e seguintes.

No PowerShell:

```powershell
Get-Content .\logs\lozgates.log -Wait
Get-Content .\logs\errors.log -Wait
```

No Linux:

```bash
tail -f logs/lozgates.log logs/errors.log
```

No Docker, os logs também aparecem em `docker compose logs ai-service` e
persistem no volume `./logs:/app/logs`.

Os dados funcionais locais ficam em `data/`: `circuito.png`, `entrada.txt`,
`logging_settings.json` e `user_activity_detailed.json`. O registro de atividade
preserva a escolha de consentimento existente e não é o mesmo que o log técnico.

## Testes

Testes automatizados no Windows/PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYGAME_HIDE_SUPPORT_PROMPT='1'
$env:SDL_VIDEODRIVER='dummy'
python -m unittest discover -v
python tests\ui_smoke.py
```

No Linux/headless:

```bash
PYTHONDONTWRITEBYTECODE=1 PYGAME_HIDE_SUPPORT_PROMPT=1 \
SDL_VIDEODRIVER=dummy python -m unittest discover -v
```

O teste de UI real abre e redimensiona a janela; execute-o somente em uma
sessão gráfica. O driver `dummy` valida desenho e regras do Pygame sem abrir uma
janela.

Para validar o fluxo integrado de navegação e simplificação em uma sessão Tk
real, usando um renderizador de circuito isolado e determinístico:

```powershell
python tests\ui_workflow_smoke.py
```

O simplificador automático aceita apenas passos que diminuem sua métrica de
complexidade, registra representações canônicas já visitadas e possui limite
defensivo de 100 passos. Expressão já reduzida ou sem regra aplicável é uma
conclusão normal, não um erro.

## Troubleshooting

- `ModuleNotFoundError`: confirme que o ambiente virtual correto está ativo e
  reinstale `requirements.txt`.
- `TclError` ou ausência de `tkinter`: instale o pacote Tk do sistema. Algumas
  distribuições portáteis de Python não incluem Tcl/Tk completo.
- janela Pygame não aparece no Linux: confirme que há `DISPLAY`/Wayland e não
  mantenha `SDL_VIDEODRIVER=dummy` fora dos testes.
- chat informa que a IA não está configurada: defina a chave ou a URL do
  serviço e reinicie o processo para reler o ambiente.
- HTTP 401/403/429 na IA: verifique a chave, acesso ao modelo e limites da conta;
  consulte `logs/errors.log`/`lozgates.log` sem copiar a chave para os logs.
- porta 8000 ocupada: altere o mapeamento de porta em `compose.yaml` e ajuste
  `LOZGATES_AI_SERVICE_URL`.
- `docker: unknown command: docker compose`: instale/ative o plugin Compose v2;
  ter apenas o binário Docker não é suficiente.
- ícone ausente ou incompatível no Linux: a inicialização ignora somente a
  aplicação do ícone e registra o diagnóstico, sem abortar a interface.

O diagnóstico original está em `docs/diagnostico-inicial.md`; o relatório da
reconstrução está em `docs/relatorio-final.md`.

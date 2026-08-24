# Relatório final — rebuilding LozGates 1.0.1

Data: 23 de agosto de 2026  
Branch: `rebuilding_lozgates`

## 1. Diagnóstico inicial

O LozGates já possuía um conjunto amplo de funcionalidades úteis, mas a
manutenção estava concentrada em poucos arquivos grandes e sem uma rede de
segurança automatizada. A interface principal tinha 1.719 linhas, combinando
navegação, estado, processamento, Pygame, simplificação e telemetria. Os módulos
lógicos eram locais; não havia banco de dados. JSON, texto e PNG na raiz eram
usados como persistência.

O baseline confirmou conversão, equivalência, árvore do simplificador e abertura
real da janela no Windows. Também mostrou caminhos dependentes do diretório de
execução, driver SDL forçado para Windows, dimensões fixas, arquivos gerados
versionados, logging baseado em terminal, IA com placeholder de chave e ausência
total de testes. O inventário anterior às mudanças permanece em
`docs/diagnostico-inicial.md`.

Tecnologias preservadas: Python, CustomTkinter/Tkinter, Pygame, Pillow, NumPy e
Requests. Não foi introduzido framework web: o serviço opcional usa a biblioteca
HTTP padrão do Python.

## 2. Bugs encontrados

1. `__pycache__` e bytecode de várias versões do Python estavam versionados.
2. A inicialização e os fluxos de circuito sobrescreviam artefatos do repositório.
3. `problems_bank.py` imprimia `None` durante qualquer import.
4. O SDL era forçado para o backend `windows`, impedindo o Pygame no Linux.
5. A superfície Pygame tinha mínimo fixo de 800x600 e não seguia o frame Tk.
6. O zoom da câmera deslocava o ponto sob o cursor.
7. A paleta podia ultrapassar os limites em superfícies pequenas.
8. A avaliação do circuito usava `eval()`, aceitando execução de Python arbitrário.
9. O analisador de lógica não tratava os aliases `*`, `+`, `~` usados pelo próprio
   LozGates e possuía precedência incorreta em combinações com implicação.
10. O analisador ignorava caracteres inválidos silenciosamente e tratava dupla
    negação incorretamente.
11. O cache do Simplificador Interativo ficava obsoleto após mudança em um filho.
12. O undo restaurava uma árvore e um alvo pertencente a outra cópia.
13. A lei distributiva era oferecida para `A+(B*C)`, mas não executava esse caso.
14. Leis inaplicáveis continuavam habilitadas, podendo produzir estado confuso.
15. O parser interativo aceitava entradas vazias ou malformadas de maneira frágil.
16. Diversos layouts absolutos cortavam conteúdo ou exigiam 1280x720.
17. Popups possuíam geometrias fixas e conteúdo sem wrap responsivo.
18. A IA tinha `Bearer COLAR CHAVE API` no código, configuração duplicada e
    tratamento inconsistente de erros.
19. Threads HTTP da IA alteravam widgets Tk diretamente.
20. Falhas HTTP, timeout e JSON inválido da IA não possuíam um contrato único.
21. Logs importantes eram apenas `print()`; não havia rotação nem arquivo de erros.
22. `except: pass` ocultava erros relevantes em caminhos de interface e atividade.
23. `front.spec` apontava para `front.py`, que não existe.
24. As dependências não tinham nenhum limite de versão.

## 3. Bugs corrigidos

- Bytecode e saídas de runtime foram removidos do índice e incluídos no
  `.gitignore`; dados novos vão para `data/` e diagnósticos para `logs/`.
- Caminhos foram centralizados com `pathlib`, e o ícone deixou de ser recriado na
  inicialização.
- O efeito colateral do import de `problems_bank.py` foi removido.
- O Pygame agora escolhe o driver por plataforma, acompanha o resize do frame e
  usa piso seguro de 320x240.
- O zoom mantém a coordenada de mundo sob o ponteiro; paleta, câmera e drawer são
  redimensionados juntos.
- `eval()` foi removido. O analisador validado suporta as duas notações, rejeita
  caracteres/sintaxe inválidos, aplica precedência e dupla negação corretamente.
- O Simplificador ganhou parser validado, cache sensível à árvore e ao conjunto de
  ignorados, undo consistente, distributiva simétrica e validação do alvo atual.
- A tela interativa só habilita leis aplicáveis, reconstrói o estado de forma
  determinística e registra conclusão uma única vez.
- Layouts principais foram migrados para pack/posicionamento relativo e funções
  centralizadas de tamanho, wrap e número de colunas.
- A IA foi isolada, configurada por ambiente e tornou-se resiliente; callbacks
  retornam ao event loop com `after()`.
- Logging técnico agora é estruturado, rotativo, persistente e captura stack trace.
- `front.spec` usa `main.py`, inclui assets e gera `LoZGates`; dependências possuem
  faixas conservadoras.

## 4. Arquitetura

### Antes

```text
interface.py monolítico
  ├─ estado/navegação/layout
  ├─ processamento local
  ├─ lifecycle Pygame dependente de Windows
  ├─ simplificador com estado global frágil
  ├─ chamada Groq e callbacks acoplados
  └─ print + JSON na raiz
```

### Depois

```text
Desktop CustomTkinter
  ├─ responsive.py + design_tokens.py
  ├─ núcleo lógico Python local
  ├─ Simplificador Interativo validado
  ├─ Pygame + platform_support.py
  ├─ AIClient/AIAssistant ─HTTP opcional─► ai-service ─► provedor
  └─ logging_config.py ─► logs rotativos

config.py ─► .env, caminhos e AISettings
data/ ─► persistência local gerada
tests/ ─► contratos críticos
```

O núcleo e o simplificador permaneceram no processo desktop por coesão e baixa
latência. Apenas a integração externa de IA foi exposta como serviço opcional:
ela tem segredo, timeout e ciclo de falha próprios. Isso cria um boundary claro
sem distribuir arbitrariamente módulos determinísticos.

## 5. Frontend

- Janela inicial limitada à área útil da tela, centralizada e maximizada quando
  suportado, sem mínimo obrigatório de 1280x720.
- Cards principais e de equivalência centralizados com dimensões relativas.
- Fluxos de home, entrada, equivalência e circuito usam pack responsivo em vez de
  uma sequência de coordenadas verticais fixas.
- Funções únicas calculam geometria, wrap e colunas para 640x480 até 4K.
- Controles do Simplificador reorganizam-se em uma, duas ou três colunas; em
  largura reduzida, ações são empilhadas.
- Popups de erro, ajuda, chat, tabela e consentimento respeitam tela e tamanho
  mínimo; mensagens longas têm wrap.
- Estados de carregamento e erros do chat foram preservados e tornados seguros.
- Hierarquia, espaçamento, dicas de entrada e feedback visual foram melhorados
  usando os tokens de design já existentes.

## 6. Simplificador Interativo

O parser recursivo agora reconhece `+`, `*`, `~` e parênteses, preserva
precedência e rejeita expressões vazias, tokens extras e agrupamentos inválidos.
O cache considera conteúdo/identidade da árvore e nós ignorados. Toda aplicação
confirma que o alvo ainda pertence à árvore, que a lei é válida e que houve
alteração real.

Undo restaura um único snapshot coerente e reinicia a busca. A distributiva
funciona nos dois sentidos oferecidos pela UI, incluindo fator comum. Foram
testadas individualmente De Morgan, identidade, nula, idempotência, inversa,
absorção e distributiva, além de equivalência lógica dos resultados.

## 7. Pygame

Foram alterados somente lifecycle, plataforma, dimensionamento, câmera,
avaliação segura e diagnóstico; componentes e interações existentes foram
preservados.

Validações realizadas:

- seleção de driver Windows/X11/Wayland/headless;
- superfície mínima e resize dinâmico;
- câmera com zoom ancorado no mouse;
- paleta dentro dos limites em 320x240, 800x600 e 1920x1080;
- renderização real em surfaces 640x360 e 1280x720;
- avaliação de `(A*B)+~C` sem `eval()`;
- payload que tentaria chamar `os.system` foi rejeitado e não executou a função.

O teste automatizado usou `SDL_VIDEODRIVER=dummy`. O smoke real carregou a
aplicação e seus módulos no Windows; o desenho e as regras específicas do Pygame
foram exercitados nas surfaces headless descritas acima, não por cliques manuais.

## 8. Linux

- Remoção de `SDL_VIDEODRIVER=windows` fixo.
- Seleção `x11` somente quando existe `DISPLAY`; no Wayland puro, decisão delegada
  ao SDL.
- Caminhos de runtime migrados para `pathlib`, sem separador `\` hardcoded.
- Aplicação de ícone tolera diferenças de plataforma sem derrubar a janela.
- Nenhum executável `.exe` ou comando de shell específico é necessário no código.
- Instruções explícitas para `python3-tk`, venv e teste headless foram adicionadas.

Não havia host Linux disponível. Instalação, janela real, sessão SDL real e
integração com provedor **não foram afirmadas como testadas em Linux**. A
compatibilidade foi validada por auditoria e testes headless das decisões de
plataforma; recomenda-se CI Linux com Xvfb como próxima camada.

## 9. Docker

Serviço criado: `ai-service`. O desktop/Pygame não foi colocado no container.

Arquivos: `Dockerfile`, `compose.yaml`, `.dockerignore`,
`requirements-service.txt` e `services/ai_service.py`. A imagem usa Python 3.12
slim, usuário sem privilégios, porta 8000, health check e volume de logs.

Comandos:

```bash
docker compose up --build -d ai-service
docker compose logs -f ai-service
docker compose down
```

`docker-compose config --quiet` validou o Compose neste host. O build real não
foi executado porque o daemon `dockerDesktopLinuxEngine` não estava ativo; o
erro ocorreu antes de processar o Dockerfile.

## 10. Logging

Local exato, por padrão:

- `logs/lozgates.log`: JSON Lines para eventos no nível configurado ou superior;
- `logs/errors.log`: JSON Lines somente para `ERROR` e `CRITICAL`, com stack trace;
- `logs/*.log.1` até o número definido em `LOZGATES_LOG_BACKUP_COUNT`.

Cada registro contém timestamp com fuso, nível, logger/módulo e mensagem. O
tamanho padrão é 2.000.000 bytes, cinco backups e nível `INFO`. Tudo é ajustável
por `.env`. O serviço escreve também no stdout, consultável com
`docker compose logs`, e em `/app/logs`, mapeado para `./logs`.

Saída textual restante em `identificar_lei.py`, `converter.py`, `tabela.py` e
ferramentas de relatório é intencional: ela compõe conteúdo de usuário/CLI e,
no simplificador direto, é capturada pela interface. Diagnósticos transitórios
dos principais fluxos foram substituídos por `logging`.

## 11. IA

### Problema original

O cliente continha um placeholder de chave, modelo/URL duplicados, callbacks
inconsistentes e alterações de Tk fora da thread principal. Falhas podiam parecer
respostas bem-sucedidas.

### Arquitetura atual

- `AISettings`: configuração central;
- `AIClient`: cliente síncrono testável para provedor ou serviço local;
- `AIAssistant`: prompts e execução assíncrona, independente de UI;
- `AIChatPopup`: somente apresentação e retorno ao event loop;
- `ai-service`: boundary HTTP opcional que mantém a chave fora do desktop.

### Configuração

Defina `LOZGATES_AI_API_KEY` ou `GROQ_API_KEY`. Para o proxy, defina também no
desktop `LOZGATES_AI_SERVICE_URL=http://127.0.0.1:8000`. URL, modelo e timeout
podem ser sobrescritos conforme a tabela do README.

### Indisponibilidade

Ausência de chave falha antes de qualquer acesso à rede. Timeout, falha de
conexão, HTTP 400/401/403/429/5xx, JSON inválido, conteúdo ausente e serviço
parado produzem mensagem amigável e log útil. A thread encerra e o desktop
continua disponível.

O contrato direto e o serviço foram testados com sessões falsas e HTTP local. A
chamada real à conta Groq não foi executada porque nenhuma chave de usuário foi
fornecida.

## 12. Testes

Resultado automatizado final executado após o refinamento: 39/39 testes
aprovados, cobrindo:

- configuração `.env`, caminhos e logging rotativo com stack trace;
- conversor, aliases, precedência, dupla negação, sintaxe e tabela-verdade;
- sete regras/estados críticos do Simplificador Interativo;
- driver, resize, câmera, paleta, desenho e avaliação segura do Pygame;
- layout em 640x480, 1024x600, 1366x768, Full HD e 4K;
- IA direta simulada, timeout, ausência de chave, resposta inválida, proxy e
  endpoints HTTP locais.

O smoke test real do Windows abriu a interface com Python 3.13/Tk 8.6.15,
redimensionou para 800x600, 1024x768 e 1600x900 e encerrou normalmente. O Python
3.12 empacotado no ambiente não tinha Tcl/Tk completo, então foi usado o Python
do sistema para a validação visual.

O último ciclo terminou em `Ran 39 tests ... OK`; não houve teste gráfico real em
Linux, chamada real à Groq nem build de imagem com daemon Docker ativo.

## 13. Arquivos importantes alterados

- `config.py`: caminhos, `.env`, ícone e `AISettings`.
- `main.py`: bootstrap previsível e logging antes da UI.
- `BackEnd/logging_config.py`: JSON Lines, rotação e arquivo de erros.
- `BackEnd/equivalencia.py`: parser/evaluador seguro e aliases.
- `BackEnd/simplificador_interativo.py`: parser, leis, cache e estado.
- `BackEnd/circuito_logico/platform_support.py`: decisão SDL multiplataforma.
- `BackEnd/circuito_logico/interactive/interactive_circuit.py`: lifecycle,
  resize e avaliação sem `eval()`.
- `BackEnd/circuito_logico/static/static_circuit.py`: embed/resize portátil.
- `BackEnd/circuito_logico/rendering/camera.py`: viewport e zoom ancorado.
- `BackEnd/ai_client.py`: contrato resiliente da IA.
- `BackEnd/ai_assistant.py`: fachada assíncrona.
- `FrontEnd/responsive.py`: cálculos compartilhados de layout.
- `FrontEnd/interface.py`: telas responsivas e estado do simplificador.
- `FrontEnd/ai_chat_popup.py`: callbacks seguros no Tk.
- `FrontEnd/logging_system.py`: dados em `data/` e diagnóstico central.
- `services/ai_service.py`: serviço HTTP opcional.
- `Dockerfile` e `compose.yaml`: imagem, health check e volume.
- `requirements*.txt`: dependências desktop, serviço e desenvolvimento.
- `front.spec`: entry point e assets corretos.
- `tests/`: regressões críticas e smoke de UI.
- `README.md`: instalação, operação, Docker, IA, logs e troubleshooting.

## 14. Pendências

1. Executar toda a matriz em um host Linux real, preferencialmente também em CI
   com Xvfb e uma sessão Wayland.
2. Iniciar o Docker Desktop e executar `docker compose up --build`, health check
   e consulta pelo desktop. O Compose está sintaticamente válido, mas a imagem
   não foi construída neste host.
3. Fazer um smoke opt-in com uma chave Groq própria para validar credenciais,
   limites e resposta do modelo no ambiente do usuário.
4. Dividir mais responsabilidades de `FrontEnd/interface.py` somente em mudanças
   futuras acompanhadas por testes de navegação; uma divisão agressiva agora
   aumentaria o risco funcional.
5. Adicionar screenshots/automação visual de Linux. Os testes atuais verificam
   cálculos de layout e desenho Pygame, não pixels de todos os widgets Tk.

Essas pendências são validações de ambiente ou evolução segura; não exigem
remover as funcionalidades preservadas nesta reconstrução.

# Auditoria do merge: `interface_update` + `web-frontend`

> **Fase 1** da reestruturação web do LoZGates. Levantamento feito em 04/10/2026, sobre o estado do GitHub
> obtido com `git fetch --all --prune` no mesmo dia. Nenhum código do projeto foi alterado e nenhuma branch
> foi criada. Caminhos relativos a `LoZGates 1.0.1/`, salvo indicação.

---

## Sumário executivo

1. **As branches se chamam `interface_update` (com underscore) e `web-frontend`** e existem só no remoto
   (`origin/…`). O ponto de divergência é `82c3128` (11/02/2026), que é o `main` atual e também a `fusion`
   e a `refatoring`.
2. **O parser canônico não está no `interface_update` nem em nenhum commit do repositório.**
   `BackEnd/core/expression_ast.py` e os três testes de regressão existem só na **Lixeira do Windows**
   (apagados em 04/10/2026, 13:43). A migração dos consumidores para ele existe só no **`stash@{0}`**
   (criado em 04/10/2026, 13:42, na branch `refatoring`) e foi feita **sobre o `main` antigo**, não sobre o
   `interface_update`. A fonte da verdade de comportamento e a fonte da verdade do parser estão separadas, e
   juntá-las é o primeiro trabalho real.
3. **O `web-frontend` é React + TypeScript + Vite rodando o Python do `main` dentro do navegador via
   Pyodide (WebAssembly), com o pygame desenhando num `<canvas>`.** Não há servidor nem API HTTP. Isso
   conflita com a regra 2 (não embutir pygame) e com a arquitetura pedida (FastAPI). A interface React pode
   ser reaproveitada. A ponte Python (`web/python/lozweb/`) não pode, porque depende de módulos do
   `FrontEnd/` do `main` que o `interface_update` já desmontou.
4. **Existe um bug de correção anterior a este trabalho**, no `main` e no `interface_update`:
   `converter_para_algebra_booleana` muda o significado de expressões como `A&B>C` (que vira `A*(~B+C)`).
   Esse conversor alimenta o circuito, as duas simplificações e a exibição em álgebra booleana. Além disso,
   o parser canônico associa `A>B>C` à esquerda e o motor do `interface_update`, à direita.
5. **O núcleo ainda guarda estado global de módulo** (o cursor de busca do `simplificador_interativo.py`).
   Num servidor com vários alunos ao mesmo tempo isso é bug de concorrência, não só dívida técnica.
6. O `interface_update` **já resolveu** parte das dívidas da Fase 3: nenhum `except:` sem tipo (o `main`
   tinha 21), todas as threads com `daemon=True` e nenhum driver `windows` fixo no código. Faltam o estado
   global, as fontes recriadas a cada frame e os `except Exception` genéricos.

**Decisões que bloqueiam a Fase 2:** D1 (restaurar o parser), D2 (FastAPI ou Pyodide) e D3 (semântica
divergente). Veja a §9.

---

## 1. Branches e histórico

### 1.1 Nomes confirmados (`git branch -a`)

| Ref | Último commit | Observação |
|---|---|---|
| `origin/interface_update` | `51bcfb7` em 06/09/2026, *style(dialogs): polish dialogs and popups with design tokens* | **O nome real tem underscore.** Não há branch local. |
| `origin/web-frontend` | `9da4fc5` em 28/09/2026, *Versão web do LoZ Gates 1.0.1 (React + Pyodide, pygame no navegador)* | Não há branch local. O autor é uma sessão do Claude Code. |
| `main`, `origin/main`, `fusion` (HEAD), `refatoring` | `82c3128` em 11/02/2026 | As quatro apontam para o mesmo commit. A working tree está limpa. |
| `origin/rebuilding_lozgates`, `origin/fix_form` | `b51cfef`, `b2f7aca` | Já estão contidas no `interface_update`. |
| `origin/lozgates-web-app`, `origin/refatorar-frontend-lozgates` | 03/03/2026, autor "v0" | Outras tentativas web (Next.js). Fora do escopo; veja D10. |
| `origin/interativo_circuito`, `origin/otavio`, locais `larissa`, `circuito_interativo`, `interativo_circuito` | 2025 | Antigas e não analisadas. |

O `fetch --prune` removeu as refs remotas `origin/circuito_interativo` e `origin/coisas-exoticas`, que já
tinham sido apagadas no GitHub. A branch local `circuito_interativo` continua intacta.

### 1.2 Ponto de divergência

- `git merge-base origin/interface_update origin/web-frontend` = **`82c3128`**, que é o `main`.
- **`interface_update`** tem 31 commits, de 23/08 a 06/09/2026:
  - 13 do Otávio, com a reconstrução: configuração centralizada, logging, simplificador finito, pygame
    multiplataforma, serviço de IA e testes.
  - 18 da Larissa, com a modularização do `FrontEnd/` em `screens/`, `components/`, `dialogs/` e
    `services/`, e o redesign com design tokens.
  - São 160 arquivos, +8.904/−4.799 linhas. O total inclui a remoção dos `.pyc` que estavam versionados.
- **`web-frontend`** tem 1 commit com 57 arquivos e +8.575 linhas, **todos dentro de `web/`** (mais 2 linhas
  no `README.md` da raiz). Nenhum `.py` fora de `web/` foi alterado, ou seja, o web roda o Python do `main`.

Consequência: um merge entre as duas não teria conflito textual, porque os arquivos não se sobrepõem. Mas
**quebraria em tempo de execução** (veja a §4.3).

---

## 2. Onde está o parser canônico (achado crítico)

### 2.1 Linha do tempo reconstruída

| Quando | O quê | Evidência |
|---|---|---|
| 22/08/2026, 15:22 a 16:59 | `BackEnd/core/expression_ast.py` criado e editado; testes `test_parser_regression.py`, `test_circuit_parser_regression.py` e `test_identificar_lei_regression.py` escritos; o pytest roda 26 testes | Datas dos arquivos na Lixeira; `.pytest_cache/v/cache/nodeids` (22/08, 16:59) |
| 22/08/2026, 15:29 | `stash@{1}` "WIP on main" (`FrontEnd/interface.py`, `TODO.md`) | `git stash list` |
| 23/08 a 06/09/2026 | O `interface_update` evolui a partir de `82c3128` **sem** esses arquivos | `git log` |
| 04/10/2026, 13:42 | `stash@{0}` "WIP on refatoring" guarda só as alterações em arquivos rastreados (a migração dos consumidores e o `TODO.md`) | `git stash show`. O stash não tem terceiro pai, então os não rastreados ficaram de fora. |
| 04/10/2026, 13:43 | Os arquivos não rastreados vão para a Lixeira. Sobram as pastas vazias `BackEnd/core/__pycache__/` e `tests/__pycache__/` | Lixeira do Windows; listagem do disco |

O git não consegue recuperar esses arquivos. Eles nunca passaram por `git add`: nenhum dos 29 blobs
inalcançáveis contém a API canônica. Também não há transcrições de sessões anteriores do Claude Code nesta
máquina.

### 2.2 O que está na Lixeira (intacto, ainda não restaurado)

| Arquivo original | Tamanho | Última edição |
|---|---|---|
| `BackEnd/core/expression_ast.py` | 7.239 B | 22/08/2026, 16:17 (**versão mais nova**) |
| `BackEnd/core/expression_ast.py` | 6.767 B | 22/08/2026, 15:22 (versão anterior, apagada em 22/08 às 15:24) |
| `tests/test_parser_regression.py` | 1.092 B | 22/08/2026, 16:49 |
| `tests/test_circuit_parser_regression.py` | 1.004 B | 22/08/2026, 16:59 |
| `tests/test_identificar_lei_regression.py` | 640 B | 22/08/2026, 16:57 |

A API do `expression_ast.py` recuperado bate com a regra 3:

- `parse`
- `Node`, `VariableNode` e `OperatorNode`, com uma ponte `valor`/`esquerda`/`direita` para o código legado
- `to_string(style="logic" | "boolean")`
- `collect_variables`, `tree_size` e `avaliar`

### 2.3 O que está no `stash@{0}` (migração dos consumidores)

| Arquivo | O que a migração fez | Problema |
|---|---|---|
| `circuito_logico/logic/parser.py` | Remove o parser local, importa `parse as criar_ast_de_expressao` e passa os operadores para `&\|!` | Está ok. **Não existe** a "redefinição local que sobrescreve o `parse`" descrita na missão, nem aqui nem no `interface_update` (que nem importa o canônico). O `circuito_logico/core/nodes.py` continua existindo. |
| `circuito_logico/rendering/circuit_renderer.py` | `op_map` passa para `&\|!` | Está ok. |
| `identificar_lei.py` | Remove o `Node` local; as leis passam a construir nós canônicos | Foi feita sobre o `main` e perde tudo que o `interface_update` adicionou: simplificação finita, distributiva dual e retorno da árvore. |
| `simplificador_interativo.py` | Remove o `Node` local, cria `_str_no()` com `to_string(style="boolean")` e filtra por `id()` | Tem a mesma perda (guard, complexidade, `_fator_comum`, checagens de identidade). Além disso, os chamadores (`interface.py`, `resolver_controller.py`, `lozweb/interativo.py`) adicionam **o nó**, e não o `id()`, em `nos_ignorados`. Com isso o botão "pular" pararia de funcionar. |
| `equivalencia.py` | `check_universal_equivalence` passa a usar `parse`/`avaliar` | Perde as validações e mensagens de erro do `interface_update`. Entrada inválida passa a levantar exceção em vez de retornar `False`. |
| `normalizer.py` | `normalize_for_comparison` passa a usar `parse`/`to_string` | **Está quebrado.** Entrega nós canônicos a `normalize_tree_variables`, que lê `.value`, `.left` e `.right` (atributos do `ExprNode`). E o `try/except` de fallback foi removido. |
| `TODO.md`, `assets/entrada.txt` | **Anotações suas**: novas pendências do simplificador e do banco de questões | Não descartar este stash. |

### 2.4 Linha de base dos testes

Rodada em cópias das branches fora do repositório, com Python 3.11.9 no Windows.

| Suíte | Resultado |
|---|---|
| Suíte do `interface_update` (`tests/`) | **60 passed**, 48 subtests passed |
| Testes recuperados da Lixeira contra o código do `interface_update` | **22 passed, 4 failed** |

Os 20 testes de `test_parser_regression.py` passam porque testam só o próprio `expression_ast`. É exatamente
o "20/20 enganoso" citado na missão. Os 4 que falham são os únicos que verificam se os consumidores produzem
nós canônicos:

- `test_usa_classes_canonicas_nao_as_antigas`
- `test_aceita_ambos_estilos_de_simbolo_com_o_mesmo_resultado`
- `test_demorgan_retorna_tipos_canonicos`
- `test_nula_retorna_variablenode`

Essas falhas provam que o `interface_update` **não está migrado**.

---

## 3. Mapa de funcionalidades

| Funcionalidade | interface_update | web-frontend | Observação |
|---|---|---|---|
| Tela inicial | Dashboard com cards ("Explorar", "Praticar") e Ajuda | `Inicio.tsx` | Mesma navegação. |
| Entrada de expressão | Campo com dica de sintaxe | `Principal.tsx` | Os dois convertem para maiúsculas e removem espaços. |
| Conversão para álgebra booleana | Sim | Sim (código do `main`) | **O conversor tem bug** nos dois (§5.2). |
| Circuito gerado da expressão | pygame gera PNG em `data/`, mais uma visualização pygame embutida no Tk | pygame gera PNG em base64 no navegador | Precisa virar layout em JSON desenhado em SVG (regra 2). |
| Salvar circuito como PNG | Diálogo de salvar | Download | Na versão nova, exportar no navegador. |
| Circuito interativo (montagem manual) | 6 modos (Livre, Portas Básicas, NAND, NOR, Avançadas, Mínimo), paleta, desfazer/refazer, validação com ESPAÇO | O mesmo pygame num `<canvas>`, com botões de atalho | A interação vai para o front; validação e simulação ficam em Python (§6). |
| Tabela-verdade | Colunas de subexpressões e conclusão (tautologia, contradição ou contingência) | Igual (código do `main`) | |
| Simplificar: Resultado (automático) | **Finita**: guard contra estados repetidos e limite de passos; sem associativa/comutativa no modo automático; distributiva dual | Versão do `main` (o TODO registra loop em `(N & H & B)\|(!F \| I)`), com o `sleep(1)` simulado | O `interface_update` é o correto. Hoje os passos chegam por `print()` e são extraídos por regex no `StepParser`. |
| Simplificar: Interativo | `ResolverController`/`ResolverState` com guard; rejeita transformação que não reduz; distributiva só por fator comum; desfazer consistente; três zonas pedagógicas | Transcrição "linha a linha" do `interface.py` do `main` | O `interface_update` é o correto. |
| Equivalência lógica | Só semântica (tabela-verdade): `A&B` contra `X&Y` dá **não equivalentes** | Semântica mais um fallback "estrutural" que renomeia variáveis: `A&B` contra `X&Y` dá **equivalentes** | **Os resultados divergem.** Veja D3d. |
| Banco de problemas | Cards redesenhados; verificação semântica mais renomeação de variáveis | Igual ao `main` | `problems_bank.py` importa `customtkinter` (dados misturados com UI). |
| Manual e ajuda interativa | `dialogs/interactive_help.py` | `dados/manual.ts` (transcrito do `main`) | Ressincronizar com a versão do `interface_update`. |
| Assistente de IA | `ai_client.py` com `AISettings` por variável de ambiente; serviço HTTP opcional (Docker) que guarda a chave no servidor | `ai_assistant.py` do `main`, com a chave em `VITE_GROQ_API_KEY` **embutida no JavaScript** | A chave fica exposta no web-frontend (o próprio README avisa). |
| Telemetria, diálogo de compartilhamento e Google Forms | `services/logging_service.py`, `services/google_forms_service.py`, `dialogs/data_sharing_dialog.py` | `logging_system.py` do `main`, arquivos no `localStorage`, botão "Encerrar sessão" | Veja D6. |
| Logging de diagnóstico, `.env` e Docker | Sim | Não | |
| Layout responsivo | `utils/responsive.py`: a janela Tk se adapta de 640×480 a 4K | Fluido, de celular a ultrawide | Só o web é responsivo de verdade. |
| Testes | 60 testes (unidade e navegação/layout com objetos falsos) | E2E com 55 verificações (puppeteer) e paridade desktop × web | A paridade do web-frontend foi feita **contra o `main`** e não vale para o `interface_update`. |

---

## 4. Como o `web-frontend` funciona hoje

### 4.1 Stack

- React 19.3, TypeScript ~5.9.3, Vite ^8.3.1 e `@vitejs/plugin-react` ^6.1.1.
- Pyodide 0.29.3 (CPython 3.13 em WebAssembly), vindo do CDN jsDelivr ou hospedado junto, com os pacotes
  `pygame-ce` e `pillow`. São cerca de 15 MB no primeiro acesso.
- `fflate` empacota o Python no build e `puppeteer-core` roda o E2E.
- Fontes IBM Plex Sans e Mono; um único `global.css` (1.443 linhas) com tokens copiados do
  `design_tokens.py`.

### 4.2 Comunicação com o "backend"

**Não há HTTP.** O React chama funções Python dentro do próprio navegador:

1. Um plugin do Vite (`vite.config.ts`) empacota `../BackEnd`, `../FrontEnd`, `../config.py` e
   `web/python/lozweb` num arquivo `lozgates-python.zip`.
2. `src/motor/pyodide.ts` carrega o Pyodide, descompacta o zip e faz `pyimport('lozweb.api')`.
3. `chamar('nome', ...args)` invoca uma função de `lozweb/api.py`, que devolve uma **string JSON**
   (`{"ok": true, ...}` ou `{"ok": false, "popup": ...}`).
4. Para rede (IA e Google Forms), `lozweb/rede.py` substitui o `requests.post` por um fluxo em duas fases:
   o Python devolve o pedido, o JS faz o `fetch` e o Python processa a resposta.
5. No circuito interativo, `lozweb/tkweb.py` imita um `tk.Frame` (`after`, `bind`, `winfo_*`) para o laço
   `frame.after(16, _tick)` rodar. Já `lozweb/plataforma.py` troca o driver SDL `windows` pelo
   `emscripten` e instala módulos `tkinter`/`customtkinter` falsos.

### 4.3 Por que a ponte Python não sobrevive ao `interface_update`

O `lozweb/` importa caminhos que **não existem mais** no `interface_update`:

| Usado pelo web-frontend (vindo do `main`) | No `interface_update` |
|---|---|
| `FrontEnd.logging_system` (`DetailedUserLogger`, `DetailedDataSharingDialog`, `ImprovedGoogleFormsSubmitter`) | `FrontEnd/services/logging_service.py`, `FrontEnd/dialogs/data_sharing_dialog.py`, `FrontEnd/services/google_forms_service.py` |
| `FrontEnd.problems_interface.IntegratedProblemsInterface` | `FrontEnd/screens/problems/problems_screen.py` |
| `FrontEnd.step_view.StepParser` | `FrontEnd/components/step_view.py` |
| Funções aninhadas de `interface.py` (transcritas em `interativo.py`) | `screens/resolver/resolver_controller.py` e `resolver_state.py` |
| `identificar_lei.time` (o relógio virtual de `passos.py`) | O `import time` foi removido |
| `config.ASSETS_PATH/"circuito.png"` | `config.CIRCUIT_IMAGE_PATH` (em `data/`) |

Além disso, `api.py` espelha o estado global do `interface.py` (`expressao_global`, `_sessao_interativa`
etc.), justamente o que a Fase 3 pede para não levar adiante.

- **Dá para reaproveitar:** a interface React (telas, modais, estado de navegação, textos do manual) e o
  harness de E2E.
- **Tem que sair:** o Pyodide, o `lozweb/`, o `tkweb` e o pygame no navegador.

---

## 5. Divergências de lógica (verificadas executando o código)

A sonda rodou sobre cópias, comparando o `expression_ast.py` recuperado com o código do `interface_update`.

### 5.1 Avaliação: canônico contra `UniversalLogicAnalyzer` (interface_update)

Os resultados são iguais em `A<>B<>C`, `A|B>C`, `A&B>C`, `!A>B`, `A>B|C`, `A<>B>C`, `!!A` e `A&B|C&D`.
A precedência `!` > `&` > `|` > `>` > `<>` é a mesma nos dois.

**Divergem em `A>B>C`.** O canônico lê `(A>B)>C` (associa à esquerda) e o `interface_update` lê `A>(B>C)`
(associa à direita):

- canônico: `[0,1,0,1,1,1,0,1]`
- interface_update: `[1,1,1,1,1,1,0,1]`

### 5.2 `converter_para_algebra_booleana` muda o significado

| Entrada | Saída do conversor | Preserva o significado? |
|---|---|---|
| `A>B` | `(~A+B)` | sim |
| `A&B>C` | `A*(~B+C)` | **não** (o correto é `~(A*B)+C`) |
| `A\|B>C` | `A+(~B+C)` | **não** |
| `A>B&C` | `(~A+B)*C` | **não** |
| `A&B<>C` | `A*((~B+C)*(~C+B))` | **não** |
| `A>B>C` | `(~(~A+B)+C)` | **não**, segundo a semântica do próprio interface_update |
| `(A>B)>C`, `!(A>B)`, `A<>B`, `!A>B` | (vários) | sim |

O conversor trabalha por cirurgia de string: procura o operando vizinho de `>`/`<>` e, sem parênteses, pega
um único caractere. No `interface_update` ele alimenta o circuito (estático e interativo), o Simplificar:
Resultado, o Simplificar: Interativo e o rótulo "Expressão em Álgebra Booleana".

### 5.3 Gramáticas diferentes

| Entrada | Canônico | Parser do simplificador (iu) | Analisador da equivalência (iu) |
|---|---|---|---|
| `AB` | erro | aceita como uma variável "AB" | erro na avaliação ("Expressão lógica malformada") |
| `A1` | erro | aceita como variável "A1" | erro na avaliação |
| `A=B` | erro | aceita como variável "A=B" | erro na avaliação |
| `A<->B` | aceita | aceita como variável "A<->B" | **erro** |
| `P_1` | erro | aceita como variável "P_1" | erro |
| `a&b` | aceita (`a` diferente de `A`) | aceita | converte para maiúsculas |

Hoje cada tela usa um parser diferente. No `interface_update` existem **sete**:

1. `simplificador_interativo.construir_arvore`
2. `identificar_lei.construir_arvore`
3. `equivalencia.UniversalLogicAnalyzer`
4. `normalizer.build_expression_tree`
5. `converter.Conversorlogical`
6. `circuito_logico/logic/parser.py`
7. `circuito_logico/core/nodes.py`, junto com o parser do circuito

### 5.4 Formato de impressão

`to_string(no, style="boolean")` reproduz exatamente o `str()` do simplificador do `interface_update`:
`(~(A+B)*C)`, `(A+(B*C))`, `~~A`. Já `str(no_canonico)` usa o estilo lógico, `(!(A|B)&C)`.

Todo `str(no)` no código migrado precisa virar uma chamada explícita a `to_string(..., style=...)`. Sem isso,
mudam os textos exibidos ao aluno e os testes do simplificador interativo, que comparam `str(...)` com
`"(~A+~B)"` etc.

### 5.5 Regra 4 reproduzida

Em `parse("(A&B)|(A&B)")`, os dois filhos são instâncias diferentes, mas `esq == dir` é `True`. Com
`ignorados = {esq}`, `dir in ignorados` também dá `True`. Com `set[int]` de `id()`, dá `False`, que é o
correto.

Há um agravante: o `OperatorNode` é **mutável** (tem setters `esquerda`/`direita`) e calcula o hash pela
estrutura. Se um nó mudar depois de entrar num `set` ou `dict`, o hash fica inconsistente.

---

## 6. Arquivos de lógica: o que diverge e qual versão vale

| Arquivo | `interface_update` | `stash@{0}` | web-frontend | Versão correta e ação |
|---|---|---|---|---|
| `BackEnd/core/expression_ast.py` | não existe | importado, mas ausente | não existe | **Lixeira** (versão das 16:17): restaurar e ajustar (D3) |
| `identificar_lei.py` | `Node` local; simplificação finita; distributiva dual | nós canônicos, sobre o `main` | igual ao `main` | **iu**, reaplicando a migração de nós e devolvendo passos estruturados, sem depender do `print` |
| `simplificador_interativo.py` | `Node` local; guard; complexidade; cursor global | canônico, sobre o `main` | igual ao `main` | **iu** com a migração: `to_string(boolean)`, `set[int]` e cursor fora do módulo |
| `equivalencia.py` | precedência corrigida; validações | via `avaliar` | igual ao `main` (precedência errada) | **iu** (semântica e mensagens), avaliando via `avaliar` |
| `normalizer.py` | `ExprNode` com parser próprio | quebrado | igual ao `main` | **iu**, reescrito sobre a AST canônica |
| `converter.py` | bug de precedência | não alterado | igual ao `main` | reescrever sobre a AST (D3b) |
| `tabela.py` | via `UniversalLogicAnalyzer` | não alterado | igual ao `main` | **iu**, via canônico |
| `circuito_logico/logic/parser.py` e `core/nodes.py` | parser e nós locais | parser removido | igual ao `main` | aplicar a intenção do **stash** sobre o **iu** e apagar `core/nodes.py` |
| `circuito_logico/rendering/*` | geometria misturada com o desenho pygame | só o `op_map` | igual ao `main` | extrair a geometria pura e devolvê-la em JSON |
| `circuito_logico/interactive/interactive_circuit.py` | validação, simulação e interação pygame/Tk juntas | não alterado | igual ao `main` | extrair validação e simulação para um módulo puro |
| `problems_bank.py` | dados junto com uma classe de UI em CTk | não alterado | igual ao `main` (com `print` na importação) | separar os dados da UI |
| `ai_assistant.py`, `ai_client.py`, `services/ai_service.py` | chave por variável de ambiente; proxy | não alterado | `main` com monkeypatch | **iu**, exposto pela API |
| `config.py` | caminhos, `AISettings`, `.env`, mais helpers de janela Tk | não alterado | `main` | **iu**; os helpers de Tk saem |

### 6.1 O que o circuito calcula hoje (e precisa continuar calculando)

- **Circuito gerado.** `calcular_layout_dinamico` monta a árvore de layout. As posições dos barramentos
  (`x = 100 + i·100`, com o barramento negado em `+40`), das portas (`NODE_H_SPACING = 180`) e dos pinos de
  entrada e saída estão hoje **dentro das funções de desenho** (`desenhar_circuito_dinamico` e
  `draw_gate_shape`). Os fios são roteados ortogonalmente pelo ponto médio (`draw_smart_wire`). Tudo isso
  vira uma função pura que devolve JSON, junto com a subexpressão de cada porta (para o hover) e o valor de
  cada fio para uma atribuição de entradas (para os "fios que acendem").
- **Circuito interativo.** A regra de correção é:
  - a saída precisa ter exatamente uma ligação;
  - todas as variáveis precisam estar conectadas (exceto no modo Mínimo);
  - precisa haver pelo menos uma porta no caminho;
  - a tabela-verdade do circuito tem que bater com a da expressão.

  A simulação propaga valores com **no máximo 15 iterações**. As restrições de cada modo (por exemplo, "só
  NAND") **só existem na paleta da interface** e não são checadas na validação. A API vai precisar
  checá-las.

---

## 7. Dependências que precisam sair

| Categoria | Onde aparece (no `interface_update`) |
|---|---|
| **Pygame** | `BackEnd/principal.py`; `circuito_logico/interactive/{components.py (pygame.Rect), interactive_circuit.py, palette.py}`; `circuito_logico/rendering/{camera.py, circuit_renderer.py, drawer.py}`; `circuito_logico/static/static_circuit.py`; `tests/test_pygame_cross_platform.py`. Código morto com pygame: `BackEnd/imagem.py` e `assets/base.py`. |
| **Tkinter/CustomTkinter fora do `FrontEnd/`** | `circuito_logico/circuit_mode_selector.py`, `interactive_circuit.py`, `static_circuit.py`, `problems_bank.py`, `config.py` (`make_window_visible_robust`, `apply_window_icon`) e `BackEnd/imagem.py` (morto). Todo o `FrontEnd/` é CTk. |
| **Plataforma** | `circuito_logico/platform_support.py` (`SDL_WINDOWID`, drivers `windows`/`x11`) e `config.apply_window_icon` (`.ico` via `iconbitmap`) somem junto com o pygame/Tk. O `SDL_VIDEODRIVER='windows'` fixo do `main` (`interactive_circuit.py:79` e `static_circuit.py:29`) já foi removido no iu. |
| **Fontes recriadas a cada chamada** | 10 chamadas a `pygame.font.Font(...)` (por exemplo, `drawer.draw_text` e as mensagens do circuito interativo). Somem com o SVG. |
| **Threads** | 4 no iu, todas com `daemon=True` (`expression_screen.py` duas vezes e `ai_assistant.py`). A API não precisa delas. |
| **Estado global** | `simplificador_interativo.py`: `_todos_os_nos_ordenados`, `_indice_no_atual` e `_chave_busca_atual`, além de `passar_pro_front`, que não tem uso. `expression_screen.py` tem cerca de 20 globais de UI, que não migram. `lozweb/api.py` espelha o `interface.py`. |
| **Exceções** | Nenhum `except:` sem tipo no iu (o `main` tem 21). Há 21 `except Exception` no `BackEnd/` do iu para estreitar durante a migração. |
| **Código morto** | `BackEnd/imagem.py`, `BackEnd/register_data.py` e `assets/base.py` (nenhum módulo importa). |

---

## 8. Riscos

| # | Risco | Impacto | Mitigação |
|---|---|---|---|
| R1 | O parser canônico só existe na Lixeira | Esvaziar a Lixeira perde o trabalho | Restaurar e commitar na primeira etapa (D1) |
| R2 | A migração do stash foi feita sobre o `main` | Aplicar o stash desfaria as correções do iu | Reaplicar a intenção, arquivo por arquivo, sobre o iu |
| R3 | Bug do conversor | Circuito e simplificações erradas para `A&B>C` e similares | Converter sobre a AST (D3b); listar essas entradas como exceções no teste de paridade |
| R4 | `A>B>C` diverge entre os motores | O resultado muda sem aviso | Decidir a associatividade (D3a) e testar |
| R5 | O `str()` canônico muda o estilo de exibição | Mudam textos na tela e testes do iu | Chamar `to_string(style=...)` explicitamente em todo consumidor |
| R6 | Cursor global no simplificador | Alunos simultâneos interferem uns nos outros | Estado por sessão ou por requisição; teste de concorrência |
| R7 | Regra 4 contra HTTP | `id()` não sobrevive entre requisições | Identificar nós por caminho na fronteira da API (D4) |
| R8 | Editor de circuito reescrito no navegador | É a maior peça nova (1.220 linhas de interação em pygame) | Lógica em Python com testes; interação em TS com E2E |
| R9 | Restrições de modo existem só na paleta | A API aceitaria um circuito NAND montado com AND | Validar as restrições no Python |
| R10 | Paridade "idêntica ao interface_update" | O código do iu vai mudar durante a migração | Oráculo congelado e lista aprovada de diferenças (D8) |
| R11 | Chave de IA dentro do bundle | Vazamento da chave | Proxy no servidor (D7) |
| R12 | Node 20.11.1 nesta máquina | O Vite 7+ exige Node ≥ 20.19 e o projeto pede Vite 8 (requisito exato a confirmar) | Atualizar para o Node 22 LTS |
| R13 | Dados de aluno na web (LGPD) | Consentimento e retenção de dados | D6 |

---

## 9. Decisões necessárias (com recomendação)

- **D1. Restaurar o parser.**
  - Copiar da Lixeira a versão de 22/08 às 16:17 e os três testes para a nova branch, e commitar em seguida.
  - Não usar o "Restaurar" do Windows, que devolveria os arquivos para a `fusion`.
  - Manter o `stash@{0}` intocado, porque ele guarda as suas anotações no `TODO.md`.
- **D2. Arquitetura web.** A missão pede FastAPI; o web-frontend usa Pyodide, sem servidor. Recomendo
  **FastAPI + React**, aproveitando a interface do web-frontend sem o Pyodide.
  - Vantagens: a API é testável com `TestClient` (Fase 5); a chave de IA fica no servidor; o celular não
    precisa baixar 15 MB de WebAssembly; dá para aproveitar o Docker do iu.
  - Custos: precisa de um servidor (UFAL, Render etc.) e o app deixa de funcionar como site estático e
    offline.
- **D3. Semântica.**
  - (a) Para `A>B>C`, recomendo **associar à direita**, que é a convenção usual e o comportamento atual do
    iu. Isso exige ajustar o canônico.
  - (b) Recomendo **corrigir o conversor** reescrevendo-o sobre a AST, aceitando que essas entradas mudem de
    resultado.
  - (c) Na gramática, recomendo:
    - variáveis de **uma letra** mais as constantes `0` e `1`;
    - entrada convertida para maiúsculas, como a interface já faz;
    - operadores `& | ! > <>` e também `* + ~ -> <->`;
    - qualquer outra coisa é erro, com mensagem clara.
  - (d) Na equivalência, recomendo manter o iu: só semântica na tela de Equivalência, com a renomeação de
    variáveis apenas no banco de problemas.
- **D4. Simplificação interativa sem estado no servidor.**
  - O cliente envia a expressão atual, os nós ignorados por caminho (índices de `children`, como `[0, 1]`)
    e o histórico, e o servidor recalcula tudo.
  - Dentro do core, `set[int]` com `id()`.
- **D5. Desktop.** A `web-unificado` passa a ser só web, com Tk e pygame removidos nela. O desktop continua
  disponível no `main` e no `interface_update` até a troca.
- **D6. Telemetria.** Manter os dados no navegador (`localStorage`), com o mesmo diálogo de consentimento e
  o envio ao Google Forms.
- **D7. IA.** Um endpoint da API faz o papel de proxy, reaproveitando `ai_client` e `AISettings`.
- **D8. Oráculo da paridade.** Congelar uma cópia somente leitura da lógica do iu em
  `tests/paridade/oraculo_interface_update/`, junto com a lista de diferenças aprovadas (D3a e D3b).
- **D9. Código morto.** Remover `imagem.py`, `register_data.py` e `assets/base.py`?
- **D10. Outras branches web.** Ignorar `lozgates-web-app` e `refatorar-frontend-lozgates` (Next.js/v0)?

---

## 10. Plano em etapas

Cada etapa termina com testes rodando e commits pequenos em português. ⏸ marca as paradas para a sua
revisão.

Estrutura proposta:

```
LoZGates 1.0.1/
├── BackEnd/
│   ├── core/             # expression_ast.py (parser canônico) e lógica pura nova
│   ├── api/              # FastAPI: valida entrada → chama o core → devolve JSON
│   ├── circuito_logico/
│   │   └── logic/        # parser.py (só o canônico), layout.py (geometria → JSON), validacao.py
│   └── *.py              # identificar_lei, simplificador_interativo, equivalencia… (mesmos nomes, já migrados)
├── frontend/             # React + TS + Vite (vindo de web/, sem Pyodide)
├── tests/
└── docs/
```

Os módulos atuais do `BackEnd/` ficam onde estão, para não quebrar os imports que os testes da Fase 5
precisam exercitar.

| Etapa | Conteúdo |
|---|---|
| **0. Salvaguarda** | Criar a `web-unificado` a partir de `origin/interface_update`; restaurar o `expression_ast.py` e os 3 testes da Lixeira; commit (D1). |
| **1. Parser definitivo** | Aplicar os ajustes da D3 (associatividade, gramática, hash e mutabilidade dos nós) e escrever os testes do próprio parser. |
| **2. Migração dos consumidores** | Um commit por arquivo, cada um com o teste que "importa do consumidor": `circuito_logico/logic/parser.py` (e apagar `core/nodes.py`), depois `identificar_lei`, `simplificador_interativo` (com o estado fora do módulo), `equivalencia`, `normalizer`, `converter` e `tabela`. Rodar o teste de paridade contra o oráculo a cada passo. |
| **3. Circuito como dados** | `layout.py` (geometria, subexpressão por porta e valor por fio) e `validacao.py` (recebe a netlist e devolve validação e simulação, checando as restrições de modo). Remover pygame e Tk do `BackEnd/`. |
| **4. API fina** | `BackEnd/api/` com: expressão, tabela-verdade, simplificação automática (com passos estruturados), simplificação interativa, equivalência, problemas, circuito (layout, modos, validar, simular) e IA. Exceções específicas viram respostas 400/422 com mensagem clara. Testes com `TestClient`. |
| **5. Frontend funcional** | `frontend/` com a interface React do web-frontend, sem Pyodide, chamando a API, com as mesmas telas e textos. ⏸ |
| **6. Identidade visual** | 2 ou 3 direções (paleta, tipografia, mock da tela inicial e da tela do circuito). ⏸ **Você escolhe** antes de implementar. Depois: circuito em SVG com zoom, pan e hover; fios que acendem; LEDs; linha do tempo da simplificação; `prefers-reduced-motion`; testes em 360, 768, 1280 e 1920 px. |
| **7. Testes e limpeza** | Suíte completa (consumidores, API, paridade e E2E); dívidas restantes da Fase 3; remoção de Tk, pygame e código morto; saída real do `pytest`. ⏸ |
| **8. Entrega** | `README.md` e `docs/relatorio-reestruturacao.md`, com a seção técnica e a de produto (com capturas de tela). |

---

## Apêndice: o que esta auditoria fez no ambiente

- No repositório, tudo foi só leitura, com duas exceções: o `git fetch --all --prune` e este arquivo (ainda
  não rastreado).
- Os arquivos da Lixeira foram **copiados** para uma pasta temporária fora do projeto, só para leitura.
  Continuam na Lixeira e não foram restaurados.
- Os testes e as sondas rodaram em cópias das branches extraídas com `git archive` para fora do
  repositório.
- Ambiente: Python 3.11.9, com pytest, FastAPI, httpx e uvicorn já instalados; Node 20.11.1; npm 10.2.4.

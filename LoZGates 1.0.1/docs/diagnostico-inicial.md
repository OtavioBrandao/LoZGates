# Diagnostico inicial do LozGates 1.0.1

Data do baseline: 23 de agosto de 2026.

## Estado observado

O LozGates e uma aplicacao desktop Python. A interface usa CustomTkinter/Tkinter,
o desenho e a edicao de circuitos usam Pygame, e as regras de logica ficam em
modulos Python locais. Nao existe banco de dados: configuracoes, atividade e
imagens intermediarias sao persistidas em JSON, texto e PNG.

O fluxo principal e:

1. `main.py` importa e inicia `FrontEnd.interface`;
2. a interface recebe uma expressao proposicional;
3. `BackEnd.converter` converte a expressao para algebra booleana;
4. o usuario acessa circuito estatico/interativo, tabela verdade, equivalencia,
   simplificacao direta ou o Simplificador Interativo;
5. `FrontEnd.logging_system` registra telemetria local opcional;
6. `BackEnd.ai_assistant` tenta consultar a API compativel com OpenAI da Groq.

## Arquitetura original

- `FrontEnd/interface.py`: composicao da janela, navegacao e orquestracao de
  praticamente todos os casos de uso (1.719 linhas).
- `FrontEnd/*`: componentes visuais, ajuda, problemas, chat e telemetria.
- `BackEnd/converter.py`, `equivalencia.py`, `tabela.py`,
  `identificar_lei.py`: processamento logico.
- `BackEnd/simplificador_interativo.py`: arvore e leis do fluxo interativo.
- `BackEnd/circuito_logico/*`: parser, renderizacao, camera, componentes e
  circuitos Pygame estatico/interativo.
- `BackEnd/ai_assistant.py`: chamada HTTP da IA acoplada ao provedor.
- arquivos JSON na raiz: configuracao e atividade local.

## Dependencias

O `requirements.txt` original declara `customtkinter`, `pygame`, `Pillow`,
`numpy` e `requests`, sem faixas de versao. Todas sao usadas. Tkinter tambem e
obrigatorio, mas e fornecido pelo sistema operacional e nao pelo PyPI.

## Problemas confirmados

1. O repositorio versiona dezenas de `__pycache__/*.pyc`, inclusive de versoes
   diferentes do Python.
2. A inicializacao recria `BackEnd/assets/icon.ico`; a geracao de circuitos e a
   entrada do usuario sobrescrevem arquivos versionados em `assets/`.
3. `BackEnd/problems_bank.py` executa um `print()` no import, causando o `None`
   observado em toda inicializacao.
4. As duas integracoes Pygame definem `SDL_VIDEODRIVER=windows`, impedindo o
   mesmo fluxo no Linux.
5. As superficies embutidas usam minimo fixo de 800x600 e nao acompanham o
   redimensionamento do frame.
6. A janela principal exige no minimo 1280x720 e as telas iniciais usam varias
   coordenadas `y` absolutas.
7. O Simplificador mantem cache global por identidade da raiz. Alteracoes em um
   filho nao mudam essa identidade e deixam referencias obsoletas no proximo
   passo.
8. O undo copia a arvore e `passo_info` separadamente. O passo restaurado aponta
   para outra copia e pode informar sucesso sem alterar a arvore visivel.
9. A lei distributiva e marcada como aplicavel para `A+(B*C)`, mas a funcao de
   aplicacao original nao implementa esse caso.
10. Todos os botoes de leis sao habilitados, mesmo quando a lei nao se aplica ao
    no atual.
11. A IA contem `Bearer COLAR CHAVE API`, nao le configuracao do ambiente e
    trata falhas de conexao como respostas bem-sucedidas.
12. Callbacks da IA alteram widgets Tk a partir da thread HTTP, operacao que nao
    e segura no Tkinter.
13. O logging diagnostico depende de `print()`; nao existem arquivos rotativos
    `lozgates.log` e `errors.log`.
14. Persistencia e configuracao usam caminhos relativos ao diretorio de onde o
    processo foi iniciado.
15. `front.spec` referencia `front.py`, arquivo inexistente.
16. Nao ha testes automatizados no baseline.

## Baseline executado

- compilacao de todos os modulos Python: sucesso;
- import de `main`: sucesso, com o efeito colateral `None`;
- conversao `A > B` para `(~A+B)`: sucesso;
- equivalencia entre `A > B` e `!A | B`: sucesso;
- construcao da arvore `(A*1)+(B*0)`: sucesso;
- inicializacao real da janela no Windows/Python 3.13 + Tk 8.6.15: permaneceu
  ativa sem excecao durante o smoke test e foi encerrada normalmente.

O runtime Python 3.12 fornecido pelo ambiente nao contem Tcl/Tk completo; por
isso o teste visual foi repetido com o Python 3.13 ja instalado no computador.
Linux nao esta disponivel neste host e devera ser validado por testes sem tela,
auditoria de plataforma e CI/container quando aplicavel.

## Partes que devem manter compatibilidade

- contratos publicos usados por `FrontEnd.interface`, especialmente
  `converter_para_algebra_booleana`, `tabela`, `principal_simplificar`,
  `construir_arvore`, `encontrar_proximo_passo` e
  `aplicar_lei_e_substituir`;
- loop Pygame embutido no frame Tk e controles de camera/circuito;
- formato das expressoes booleanas (`*`, `+`, `~`);
- navegacao para tabela, equivalencia, banco de problemas e os dois modos de
  simplificacao;
- telemetria local opt-in/opt-out ja exposta ao usuario.

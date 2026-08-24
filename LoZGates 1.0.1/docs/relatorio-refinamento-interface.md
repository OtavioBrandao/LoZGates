# Relatório — correção do simplificador e refinamento da interface

Data: 23 de agosto de 2026  
Branch: `rebuilding_lozgates`

## Simplificador

### Causa do loop

O caso informado foi reproduzido antes da alteração. O motor de simplificação
direta aplicava todas as leis recursivamente e chamava a si próprio sempre que a
string mudava. Associatividade reorganizava a árvore sem reduzi-la e a
comutatividade voltava a ordenar subárvores intermediárias. Não existiam estados
visitados, métrica de progresso ou limite.

Para a expressão:

```text
((A & B) | (A & !B)) | ((A & C) | (A & !C)) | (A & D)
```

o baseline produziu 5.955 linhas de transformações repetidas e terminou apenas
com `maximum recursion depth exceeded`, apresentado incorretamente como erro de
sintaxe.

### Algoritmo anterior

1. Simplificava recursivamente os filhos.
2. Aplicava em sequência leis redutoras e leis apenas reorganizadoras.
3. Se a representação textual mudasse, chamava novamente a função recursiva.
4. O laço externo repetia até a string permanecer igual.

Uma mudança textual era suficiente para continuar, mesmo com a mesma ou maior
complexidade.

### Alterações realizadas

- Uma travessia aplica no máximo uma regra redutora por passo.
- Cada candidato é produzido em uma cópia da última árvore válida.
- A métrica contabiliza nós, operadores, literais e penalidades estruturais para
  negação composta, associação à esquerda e ordem não canônica.
- O passo só é aceito se `complexidade_nova < complexidade_atual`.
- A representação canônica achata AND/OR associativos e ordena operandos
  comutativos antes de consultar `visited_states`.
- A distributiva automática foi limitada à extração de fator comum, incluindo o
  caso dual `(A&B)|(A&C) -> A&(B|C)`. Expansões que aumentam a árvore deixaram de
  ser oferecidas como simplificação.
- O processo automático removeu `sleep(1)` e roda na thread daemon já destinada
  ao trabalho.
- Uma fila entrega linhas de progresso ao `after()` do Tk. Nenhum widget é
  alterado pela thread secundária.
- O modo interativo usa o mesmo guard de complexidade/estados, desabilita os
  botões durante cada ação e mantém o último snapshot válido em qualquer parada.
- Logs foram adicionados para início, regra aplicada, conclusão, ausência de
  regra, repetição, falta de progresso, limite e exceção.

### Critérios de parada

1. Árvore final atômica (`A`, `!A`, `0` ou `1`, conforme a entrada).
2. Nenhuma regra capaz de reduzir a complexidade.
3. Representação canônica já presente em `visited_states`.
4. Transformação sem redução real.
5. `MAX_SIMPLIFICATION_STEPS = 100`.
6. Exceção capturada, registrada e apresentada sem fechar a aplicação.

Ao atingir repetição ou limite, a árvore candidata é descartada e a última
expressão aceita permanece visível.

### Casos testados

| Entrada | Resultado | Situação |
| --- | --- | --- |
| expressão grande informada | `A` | 8 passos finitos |
| `A | !A` | `1` | complementaridade |
| `A | (A & B)` | `A` | absorção |
| `A & B` | `(A&B)` | término normal sem redução |
| `((A | B) & 1) | ((A | B) & 0)` | `(A|B)` | expressão complexa finita |
| `(A&1)&1`, limite 1 | `(A&1)` | última expressão válida preservada |

Também foram testados diretamente os motivos `repeated_state`, `no_progress` e
`maximum_steps`, além da redução de complexidade de todas as leis aceitas pelo
modo interativo.

## Navegação

### Causa

`trocar_para_abas()` executava somente `show_frame(frame_abas)`. O `CTkTabview`
preservava sua seleção anterior; portanto “Ver Circuito” levantava o container,
mas não selecionava a aba Circuito.

### Mudança

`FrontEnd/navigation.py` introduz `NavigationController`, que mantém
`current_view` e centraliza:

- elevação de frames;
- seleção explícita de `circuit`, `interactive_circuit` e `expression`;
- sincronização quando o usuário troca a aba pelo controle visual.

`trocar_para_abas(target_view="circuit")` agora chama `show_tab(target_view)`.
Assim, “Ver Circuito” sempre seleciona Circuito; ações do banco de problemas
podem solicitar Expressão explicitamente. Depois disso, o usuário continua
livre para alternar qualquer aba.

Os nomes visuais das abas também foram centralizados como constantes, evitando
comparações duplicadas com strings preenchidas por espaços.

## CustomTkinter

Telas e componentes modificados:

- container principal de abas;
- cabeçalho e imagem do circuito estático;
- tela de resultado da simplificação;
- histórico/rodapé de passos;
- controles de leis do Simplificador Interativo.

Melhorias:

- o Tabview recebeu padding uniforme;
- a expressão no cabeçalho do circuito ajusta o wrap à largura disponível;
- o PNG do circuito é redimensionado proporcionalmente após debounce de resize;
- a imagem usa `CTkImage`, compatível com escalonamento HiDPI;
- a espera ativa do PNG foi substituída por polling `after()` sem bloquear Tk;
- “Ver Circuito” muda para `Processando...`, rejeita clique duplicado e sempre é
  restaurado, inclusive após falha;
- o simplificador mostra estado de processamento, bloqueia retorno durante o
  worker e restaura os controles ao finalizar;
- o rodapé de resultado usa corretamente `grid_remove()`, evitando estado visual
  antigo ao repetir o fluxo;
- os botões interativos continuam usando a fábrica e os design tokens existentes,
  com reflow em grid de uma a três colunas;
- os únicos `place()` restantes são três cards centralizados com `relx/rely`, não
  coordenadas absolutas fixas. Os elementos internos usam pack/grid e padding.

## Testes executados

### Automatizados

```text
python -m unittest discover -v
Ran 39 tests
OK
```

Cobertura nova desta etapa:

- grande redução até `A`;
- complementaridade, absorção, expressão já reduzida e expressão complexa;
- limite defensivo e preservação da última árvore;
- estado repetido, não progresso e complexidade de todas as leis interativas;
- distributiva redutora versus expansão rejeitada;
- `NavigationController` abrindo Circuito e permitindo navegação posterior.

### Tk real no Windows

Com Python 3.13 e Tk 8.6.15:

1. `tests/ui_smoke.py`: redimensionou a janela para 800x600, 1024x768 e
   1600x900; alternou Expressão → Circuito → Expressão.
2. `tests/ui_workflow_smoke.py`: em uma janela real, confirmou a expressão grande,
   acionou Ver Circuito, confirmou `current_view == "circuit"`, foi para
   Expressão, executou a simplificação, exibiu resultado `A` e voltou a navegar.
   O ciclo completo foi repetido duas vezes na mesma janela.

O workflow gráfico substitui somente a escrita do PNG por um renderizador local
determinístico, para testar estado e callbacks da UI. O Pygame real continuou
coberto pela suíte headless existente: driver, surfaces 640x360/1280x720, câmera,
paleta, desenho e avaliação segura. Não foi realizado clique manual no circuito
Pygame embutido nesta etapa, e isso não é apresentado como testado.

## Commits

- `24bef10 fix: guarantee finite boolean simplification`
- `4788ca0 fix: select circuit view and keep Tk workflows responsive`

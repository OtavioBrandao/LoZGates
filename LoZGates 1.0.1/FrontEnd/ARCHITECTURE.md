# Arquitetura do FrontEnd

## Visão Geral

O projeto está passando por uma reestruturação para modularizar o interface.py e melhorar a manutenibilidade. A estrutura final almejada é:

- **main.py**: Ponto de entrada do sistema.
- **FrontEnd/app/loz_app.py**: Classe base da interface (em andamento).
- **FrontEnd/app/navigation.py**: Controle centralizado de navegação entre telas.
- **FrontEnd/screens/**: Telas principais e controladores.
  - home/: Tela inicial.
  - equivalence/: Tela e controle da Equivalência Lógica.
  - circuit/: Tela e controle da integração com Pygame para o Circuito Interativo.
- **FrontEnd/services/**: Lógica de serviços (logging, forms, etc.).
- **FrontEnd/styles/**: Design tokens e estilos centralizados.
- **FrontEnd/dialogs/**: Popups customizados.
- **FrontEnd/utils/**: Funções auxiliares (responsividade).

## Status da Migração (Etapa 4 Concluída)

- Serviços de Logging, Forms, Estilos e Popups extraídos (Etapa 2).
- Navegação padronizada e Tela Inicial extraída (Etapa 3).
- **Equivalência Lógica**: Modularizada para EquivalenceScreen e EquivalenceController em screens/equivalence/.
- **Circuito Interativo**: Modularizado para CircuitScreen e CircuitController em screens/circuit/, encapsulando o seletor sem quebrar a renderização assíncrona do Pygame.
- As integrações do Motor Lógico (BackEnd) e Motor Gráfico (Pygame) foram isoladas nos Controllers, aliviando o interface.py.

## Regras Críticas de Manutenção
- **Pygame Lifecycle**: A inicialização do circuito ocorre de maneira injetada e assíncrona, usando loops não bloqueantes .after() ou Threads. Não reescreva o CircuitModeSelector no momento. O Controller apenas instancia e despacha.
- O sistema de **Resolver Interativo (Simplificação e Leis)** ainda reside em interface.py e é fortemente acoplado à árvore matemática; ele será extraído nas próximas etapas.

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

## Status da Migração (Etapa 6 Concluída)

- Serviços de Logging, Forms, Estilos e Popups extraídos (Etapa 2).
- Navegação padronizada e Tela Inicial extraída (Etapa 3).
- **Equivalência Lógica**: Modularizada para EquivalenceScreen e EquivalenceController em screens/equivalence/.
- **Circuito Interativo**: Modularizado para CircuitScreen e CircuitController em screens/circuit/, encapsulando o seletor sem quebrar a renderização assíncrona do Pygame.
- **Resolver Interativo (Simplificação e Leis)**: Extraído para `ResolverScreen`, `ResolverController` e `ResolverState` na pasta `screens/resolver/` (Etapa 5).
- **Interface Geral**: Migrada e convertida. O módulo original `interface.py` agora serve apenas como um ponto de injeção (fachada) para inicializar a nova arquitetura centralizada em `LOZGatesApp` e `LegacyExpressionScreen` (Etapa 6).
- **Componentes**: Todos os widgets (`buttons.py`, `step_view.py`) migrados para `components/`.

## Regras Críticas de Manutenção
- **Pygame Lifecycle**: A inicialização do circuito ocorre de maneira injetada e assíncrona, usando loops não bloqueantes .after() ou Threads. O Controller apenas instancia e despacha.
- A árvore matemática (`simplification_guard`) é injetada no controlador do Resolver.
- As responsabilidades estão perfeitamente divididas em Model-View-Controller, mantendo a consistência com o BackEnd sem introduzir acoplamentos.

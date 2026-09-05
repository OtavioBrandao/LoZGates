# Arquitetura do FrontEnd

## Visão Geral

O projeto está passando por uma reestruturação para modularizar o `interface.py` e melhorar a manutenibilidade. A estrutura final almejada é:

- **`main.py`**: Ponto de entrada do sistema.
- **`FrontEnd/app/loz_app.py`**: Classe base da interface (em andamento).
- **`FrontEnd/app/navigation.py`**: Controle centralizado de navegação entre telas.
- **`FrontEnd/screens/`**: Telas principais.
  - `home/`: Tela inicial.
- **`FrontEnd/services/`**: Lógica de serviços (logging, forms, etc.).
- **`FrontEnd/styles/`**: Design tokens e estilos centralizados.
- **`FrontEnd/dialogs/`**: Popups customizados.
- **`FrontEnd/utils/`**: Funções auxiliares (responsividade).

## Status da Migração (Etapa 3)

- Serviços de Logging e Forms extraídos.
- Estilos e Popups extraídos.
- Navegação padronizada com `NavigationController`.
- A Tela Inicial (`HomeScreen`) foi encapsulada com sucesso.
- Telas complexas como Equivalência e Circuito ainda estão em `interface.py` e devem ser extraídas nas próximas etapas.

## Regras de Manutenção
- Não utilizar cat ou edições inline diretas sem verificar a estrutura com antecedência.
- O sistema de Circuitos, Resolver e Equivalência **ainda** estão muito acoplados. Qualquer extração deve preservar as regras de negócios exatas (ex: closure dependencies em `interface.py`).

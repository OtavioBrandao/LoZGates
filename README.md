LoZ Gates: Ferramenta Educacional de Lógica
Uma aplicação desktop desenvolvida para auxiliar no estudo da Lógica Proposicional, Álgebra Booleana e Circuitos Digitais. A ferramenta oferece uma interface gráfica amigável onde os usuários podem inserir expressões lógicas e visualizar suas representações, simplificações e propriedades de forma interativa.

📜 Sumário
Visão Geral

Funcionalidades Principais

Tecnologias Utilizadas

Como Executar o Projeto

Pré-requisitos

Instalação

Execução

Estrutura do Projeto

Autores

Agradecimentos

🖼️ Visão Geral
O "LoZ Gates" foi criado como uma ferramenta de apoio ao aprendizado, permitindo que estudantes possam praticar e compreender melhor os conceitos que interligam a lógica matemática e a eletrônica digital.

(Sugestão: Adicione aqui um GIF ou screenshots da aplicação em funcionamento para um README mais atrativo!)

✨ Funcionalidades Principais
Visualização de Circuitos Lógicos: Gera e exibe o circuito digital correspondente a uma expressão lógica proposicional.

Tabela Verdade: Cria a tabela verdade completa para qualquer expressão, identificando se é uma tautologia, contradição ou contingência.

Simplificação de Expressões: Simplifica expressões lógicas passo a passo, mostrando as leis de equivalência (De Morgan, Distributiva, etc.) aplicadas em cada etapa.

Verificação de Equivalência: Compara duas expressões lógicas e determina se são equivalentes.

Conversão para Álgebra Booleana: Converte expressões da lógica proposicional (com símbolos como &, |, !) para o formato de Álgebra Booleana (*, +, ~).

Interface Gráfica Intuitiva: Todas as funcionalidades são acessíveis através de uma interface moderna e fácil de usar.

Ajuda com IA: Integração com um clique para enviar a expressão a uma IA (como o ChatGPT) para obter explicações detalhadas.

🛠️ Tecnologias Utilizadas
Python: Linguagem principal do projeto.

CustomTkinter: Biblioteca para a criação da interface gráfica moderna.

Pygame: Utilizado para desenhar e renderizar os circuitos lógicos dinamicamente.

Pillow (PIL): Usado para manipulação de imagens, como salvar os circuitos gerados e criar ícones.

🚀 Como Executar o Projeto
Siga os passos abaixo para executar a aplicação em sua máquina local.

Pré-requisitos
Python 3.8 ou superior

pip (gerenciador de pacotes do Python)

Instalação



Execução


📂 Estrutura do Projeto
O projeto é organizado nos seguintes arquivos principais:

interface.py: Ponto de entrada da aplicação. Responsável por criar todas as janelas, abas, botões e interações com o usuário usando CustomTkinter.

circuito_logico.py: Utiliza Pygame para desenhar a árvore de sintaxe abstrata (AST) de uma expressão como um circuito lógico, salvando o resultado como uma imagem.

identificar_lei.py: Contém a lógica para a simplificação automática de expressões booleanas. Percorre a árvore da expressão e aplica um conjunto de leis lógicas de forma recursiva até não ser mais possível simplificar.

simplificador_interativo.py: Uma versão interativa do simplificador que permite ao usuário escolher qual lei lógica aplicar em cada passo, sendo executado via terminal atualmente.


👨‍💻 Autores
Este projeto foi desenvolvido por:

Larissa de Souza

Otávio Menezes

Zilderlan Santos

David Oliveira

🙏 Agradecimentos
Um agradecimento especial ao Professor Doutor Evandro de Barros Costa e à Universidade Federal de Alagoas (UFAL) - Instituto de Computação, pelo apoio e orientação durante o desenvolvimento deste projeto.

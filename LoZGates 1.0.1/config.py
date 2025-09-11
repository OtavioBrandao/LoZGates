import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(ROOT_DIR, "assets")

informacoes = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 Alunos responsáveis:
- Larissa de Souza
- Otávio Menezes
- Zilderlan Santos
- David Oliveira
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 Átomos aceitos:
P, Q, R, S, T

🔣 Símbolos lógicos utilizados:
- '&'  → E (conjunção)
- '|'  → OU (disjunção)
- '!'  → NÃO (negação)
- '>'  → IMPLICA (condicional)

⚠️ Atenção!
Ao digitar a expressão, o usuário deve indicar **qual é a operação raiz** da expressão.

📝 Exemplo:
    (P & Q) | ((P | Q) & (R | S))

- ((P > Q) & (R | S)) é uma subexpressão
- (P & Q) é outra subexpressão
➡ O operador que conecta as duas é o **'|'**, que representa a **operação raiz** da expressão.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠️ Funcionalidades disponíveis:
1. Visualizar o circuito lógico equivalente
2. Gerar a tabela verdade
3. Converter a expressão para Álgebra Booleana e comparar
4. Simplificar a expressão lógica proposicional
5. Verificar se duas expressões são logicamente equivalentes
6. Obter ajuda da IA para simplificação

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Motivação:
A proposta é desenvolver uma aplicação com interface amigável que ajude os alunos a compreenderem as interações entre **Lógica Proposicional** e **Circuitos Digitais**. Essa ferramenta visa promover o aprendizado prático e interdisciplinar, conectando conceitos de diferentes áreas.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏛️ Universidade Federal de Alagoas  
🏢 Instituto de Computação  
👨‍🏫 Prof. Dr. Evandro de Barros Costa
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

duvida_circuitos = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- O termo '~' corresponde ao '!' que é uma NEGAÇÃO.
- O implica é representado por '>' e pode ser escrito como NOT P or Q no caso de 'P>Q'
- O circuito abaixo está sendo representado no formato de corda de violão para melhor entendimento
- AND (*): A saída é verdadeira apenas quando todas as entradas forem verdadeiras.
- OR (+): A saída é verdadeira quando pelo menos uma entrada for verdadeira.
- NOT (!): Inverte o valor lógico da entrada.
- Dica: Para entender o comportamento do circuito, use a tabela verdade para visualizar como diferentes combinações de entradas afetam a saída.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
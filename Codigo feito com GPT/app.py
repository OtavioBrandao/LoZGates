import os
from flask import Flask, render_template, request
from sympy.logic.boolalg import And, Or, Not
from sympy import symbols, sympify
from graphviz import Digraph

app = Flask(__name__)

# Caminho para a pasta de imagens no diretório atual
IMAGES_FOLDER = os.path.abspath(os.path.join(os.getcwd(), 'static', 'images'))
os.makedirs(IMAGES_FOLDER, exist_ok=True)  # Cria o diretório se não existir

# Função para validar a expressão
def validar_expressao(expressao):
    stack = []
    for char in expressao:
        if char == "(":
            stack.append(char)
        elif char == ")":
            if not stack:
                return False
            stack.pop()
    return len(stack) == 0

# Função para formatar a expressão lógica
def formatar_expressao(expressao_logica):
    return expressao_logica.replace("&", "^").replace("|", "v").replace("~", "¬")

# Função para avaliar a expressão lógica
def avaliar_expressao(expressao_logica):
    variaveis = {char: symbols(char) for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
    return sympify(expressao_logica, locals=variaveis)

# Função para gerar o circuito lógico
def gerar_circuito(expressao_logica):
    expressao = avaliar_expressao(expressao_logica)
    dot = Digraph(comment='Circuito Lógico')
    dot.attr(rankdir='LR')

    def criar_nodos(expr, parent=None):
        if expr.is_Symbol:
            node_id = str(expr)
            dot.node(node_id, label=str(expr), shape='circle', color='lightblue', style='filled')
            if parent:
                dot.edge(node_id, parent)
            return node_id

        if isinstance(expr, Not):
            child = criar_nodos(expr.args[0])
            node_id = f"NOT_{id(expr)}"
            dot.node(node_id, label='NOT', shape='triangle', color='red', style='filled')
            dot.edge(child, node_id)
            if parent:
                dot.edge(node_id, parent)
            return node_id

        if isinstance(expr, And):
            left = criar_nodos(expr.args[0])
            right = criar_nodos(expr.args[1])
            node_id = f"AND_{id(expr)}"
            dot.node(node_id, label='AND', shape='box', color='green', style='filled')
            dot.edge(left, node_id)
            dot.edge(right, node_id)
            if parent:
                dot.edge(node_id, parent)
            return node_id

        if isinstance(expr, Or):
            left = criar_nodos(expr.args[0])
            right = criar_nodos(expr.args[1])
            node_id = f"OR_{id(expr)}"
            dot.node(node_id, label='OR', shape='box', color='yellow', style='filled')
            dot.edge(left, node_id)
            dot.edge(right, node_id)
            if parent:
                dot.edge(node_id, parent)
            return node_id

    criar_nodos(expressao)

    output_image_path = os.path.join(IMAGES_FOLDER, 'circuito_logico')
    dot.render(output_image_path, format='png', cleanup=True)

    return f"/static/images/circuito_logico.png"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        expressao_logica = request.form["expressao"]

        if not validar_expressao(expressao_logica):
            return render_template("index.html", error="Expressão inválida: Parênteses desbalanceados ou operadores incorretos.")

        try:
            expressao_formatada = formatar_expressao(expressao_logica)
            image_path = gerar_circuito(expressao_logica)

            # Geração da explicação como texto
            explicacao = f"A expressão lógica '{expressao_formatada}' foi convertida em um circuito lógico com portas AND, OR e NOT."

            return render_template(
                "index.html",
                image_path=image_path,
                explicacao=explicacao,
                expressao_formatada=expressao_formatada
            )
        except Exception as e:
            return render_template("index.html", error=f"Erro ao processar a expressão: {e}")

    return render_template("index.html", image_path=None, explicacao=None, expressao_formatada=None)

if __name__ == "__main__":
    app.run(debug=True)

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

print("ygor")

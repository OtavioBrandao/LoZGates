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

import os
from FrontEnd.interface import inicializar_interface

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(ROOT_DIR, "assets")

if __name__ == "__main__":
    inicializar_interface()

"""Acesso ao oráculo congelado do interface_update (ver oraculo_interface_update/LEIA-ME.md)."""
import ast
import importlib
import json
import logging
import pathlib

PACOTE = "tests.paridade.oraculo_interface_update"
PASTA = pathlib.Path(__file__).parent / "oraculo_interface_update"


def manifesto():
    return json.loads((PASTA / "MANIFESTO.json").read_text(encoding="utf-8"))


def modulo(caminho_pontilhado):
    """Ex.: modulo('BackEnd.equivalencia') carrega a cópia congelada."""
    return importlib.import_module(f"{PACOTE}.{caminho_pontilhado}")


def validar_resposta_problema():
    """
    A regra de correção do banco de problemas mora dentro de uma tela
    CustomTkinter. Extraímos o método original do código-fonte congelado e o
    compilamos sozinho, sem importar a interface.
    """
    fonte = (PASTA / "FrontEnd" / "screens" / "problems" / "problems_screen.py").read_text(encoding="utf-8")
    arvore = ast.parse(fonte)
    metodo = next(
        no for no in ast.walk(arvore)
        if isinstance(no, ast.FunctionDef) and no.name == "validate_answer_with_equivalence"
    )
    modulo_isolado = ast.Module(body=[metodo], type_ignores=[])
    espaco = {"logger": logging.getLogger("oraculo.problems")}
    exec(compile(modulo_isolado, "problems_screen.py(oráculo)", "exec"), espaco)
    funcao = espaco["validate_answer_with_equivalence"]
    return lambda resposta, correta: funcao(None, resposta, correta)

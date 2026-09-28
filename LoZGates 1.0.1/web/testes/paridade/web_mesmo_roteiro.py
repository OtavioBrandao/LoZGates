import os, sys, json, io, contextlib
"""Executa no lozweb (versão web) o mesmo roteiro de cliques do desktop_original.py."""
from pathlib import Path
APP = str(Path(__file__).resolve().parents[3])
os.environ["LOZGATES_APP_DIR"] = APP
os.environ["LOZGATES_DADOS_DIR"] = sys.argv[2]
sys.path.insert(0, APP + "/web/python")
from lozweb import api
roteiro = json.loads(sys.argv[1])
q = lambda f, *a: json.loads(f(*a))
def cartao(c):
    if c["tipo"] == "inicial": return [c["titulo"], c["expressao"]]
    if c["tipo"] == "pular": return [c["titulo"], c["texto"]]
    return [c["titulo"]] + ([c["subexpressao"]] if c["subexpressao"] else []) + [c["transformacao"], c["status"]]
def norm(r):
    e = r["estado"]
    return {"expressao": e["expressao"], "analise": e["analise"]["texto"], "cartoes": [cartao(c) for c in e["cartoes"]],
            "leis_habilitadas": e["leis_habilitadas"], "pular_habilitado": e["pular_habilitado"], "desfazer_habilitado": e["desfazer_habilitado"]}
saida = []
with contextlib.redirect_stdout(io.StringIO()):
    q(api.iniciar); q(api.confirmar_expressao, roteiro["expressao"]); q(api.trocar_para_abas, roteiro["expressao"])
    q(api.expressao_convertida, roteiro["expressao"])
    r = q(api.interativo_iniciar)
    saida.append({"acao": "iniciar", "estado": norm(r), "popups": r["popups"]})
    for acao in roteiro["acoes"]:
        e = saida[-1]["estado"]
        habilitado = {"pular": e["pular_habilitado"], "desfazer": e["desfazer_habilitado"]}.get(acao, e["leis_habilitadas"])
        if not habilitado:
            saida.append({"acao": acao, "estado": e, "popups": []}); continue
        r = q({"pular": api.interativo_pular, "desfazer": api.interativo_desfazer}.get(acao, api.interativo_lei), *([] if acao in ("pular","desfazer") else [int(acao)]))
        saida.append({"acao": acao, "estado": norm(r), "popups": r["popups"]})
print("@@JSON@@" + json.dumps(saida, ensure_ascii=False))

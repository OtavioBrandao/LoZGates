"""
Compara os cartões do "Simplificar - Resultado" (StepView) do desktop ORIGINAL com a versão web.
  PYTHON_DESKTOP=python3 python comparar_resultado.py
"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
N = os.path.dirname(os.path.abspath(__file__))
APP = str(Path(__file__).resolve().parents[3])
PY_DESKTOP = os.environ.get("PYTHON_DESKTOP", sys.executable)
XVFB = ["xvfb-run", "-a"] if (not os.environ.get("DISPLAY") and shutil.which("xvfb-run") and os.name != "nt") else []
TMP = tempfile.mkdtemp(prefix="lozgates-paridade-")
exprs = ["(a&b)|(a&!b)", "!(A&B)|(A&A)", "(p>q)&p", "(A|B)&(A|C)", "A&!A|B", "((A&B)|C)>(D<>E)"]
DESK = r'''
import sys, json
__file__ = sys.argv[1]  # desktop_original.py calcula o caminho do app a partir do próprio arquivo
exec(open(sys.argv[1], encoding="utf-8").read().split("roteiro = json.loads")[0])
expr = sys.argv[3]
processar()
botao("💡Circuitos e Expressões").invoke(); processar()
e = entrada(); e.insert(0, expr)
botao("✅Confirmar").invoke(); processar()
botao("🔌Ver Circuito").invoke(); processar(40); popups()
[w for w in todos(janela) if isinstance(w, ctk.CTkTabview)][0].set("      Expressão      "); processar()
botao("🔗Realizar conversão").invoke(); processar()
botao("🔍Simplificar - Resultado").invoke(); processar(40)
sv = [w for w in todos(janela) if type(w).__name__ == "StepView"][0]
cartoes = [[texto_de(l) for l in todos(f) if isinstance(l, ctk.CTkLabel) and texto_de(l)] for f in sv.scroll_area.winfo_children()]
rodape = [texto_de(l) for l in todos(sv.footer) if isinstance(l, ctk.CTkLabel) and texto_de(l)]
print("@@JSON@@" + json.dumps({"cartoes": cartoes, "rodape": rodape}, ensure_ascii=False))
'''
open(f"{TMP}/desk_resultado.py", "w", encoding="utf-8").write(DESK)
desk = {}
for expr in exprs:
    os.makedirs(f"{TMP}/desk", exist_ok=True)
    out = subprocess.run(XVFB + [PY_DESKTOP, f"{TMP}/desk_resultado.py", f"{N}/desktop_original.py", f"{TMP}/desk", expr], capture_output=True, text=True, timeout=300)
    if "@@JSON@@" not in out.stdout: print(out.stdout[-1500:], out.stderr[-2500:]); sys.exit(1)
    desk[expr] = json.loads(out.stdout.split("@@JSON@@")[1])
sys.path.insert(0, os.path.join(APP, "web", "python"))
os.environ["LOZGATES_APP_DIR"] = APP; os.environ["LOZGATES_DADOS_DIR"] = f"{TMP}/web"
import io, contextlib
from lozweb import api
with contextlib.redirect_stdout(io.StringIO()): api.iniciar()
total = 0
for expr in exprs:
    with contextlib.redirect_stdout(io.StringIO()): r = json.loads(api.simplificar_resultado(expr))
    cartoes = [["Expressão Inicial", r["expressao_inicial"]]] + [[f"Iteração {p['iteration']} — {p['law']}"] + ([f"Subexpressão: {p['subexpression']}"] if p.get("subexpression") else []) + [f"{p['before']} → {p['after']}", f"{'✔' if p['success'] else '✖'} {p['result_expression']}" if p.get('result_expression') else ('✔' if p['success'] else '✖')] for p in r["passos"]]
    f = r["final"]; rodape = ["Expressão Resultante", f["expressao"]] + (["Nenhuma simplificação adicional foi identificada."] if (not f["sucesso"] or not r["passos"]) else []) + ([f"Iterações: {len(r['passos'])}"] if r["passos"] else [])
    iguais = cartoes == desk[expr]["cartoes"] and rodape == desk[expr]["rodape"]
    total += not iguais
    ritmo = [p["t"] for p in r["passos"]]
    print(f"{expr:>18}: {'IGUAL' if iguais else 'DIFERENTE'} ({len(cartoes)-1} passos, resultado {f['expressao']}, instantes {ritmo} s, fim {f['t']} s)")
    if not iguais: print("   desk:", desk[expr]); print("   web :", {"cartoes": cartoes, "rodape": rodape})
print("EXPRESSÕES DIFERENTES:", total)
sys.exit(1 if total else 0)

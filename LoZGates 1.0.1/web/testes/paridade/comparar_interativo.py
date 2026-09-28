"""
Compara, clique a clique, o modo "Simplificar - Interativo" do desktop ORIGINAL
(FrontEnd/interface.py rodando de verdade) com a versão web (lozweb).

  PYTHON_DESKTOP=python3 python comparar_interativo.py
Precisa de customtkinter, pygame(-ce), Pillow e numpy no Python do desktop. Sem monitor
(Linux/CI), usa xvfb-run automaticamente.
"""
import json, subprocess, sys, shutil, os, tempfile
N = os.path.dirname(os.path.abspath(__file__))
PY_DESKTOP = os.environ.get("PYTHON_DESKTOP", sys.executable)
XVFB = ["xvfb-run", "-a"] if (not os.environ.get("DISPLAY") and shutil.which("xvfb-run") and os.name != "nt") else []
TMP = tempfile.mkdtemp(prefix="lozgates-paridade-")
leis = [str(i) for i in range(9)]
roteiros = [
  {"expressao": "(a&b)|!c", "acoes": ["pular","desfazer"] + leis + ["pular"] + leis + ["pular"] + leis + ["pular"] + leis + ["desfazer","desfazer","8","pular","desfazer"]},
  {"expressao": "!(A&B)|(A&A)", "acoes": leis + ["pular"] + leis + ["pular"] + leis + ["desfazer"] + leis + ["pular"] + leis},
  {"expressao": "(p>q)&p", "acoes": (leis + ["pular"]) * 4 + ["desfazer", "desfazer", "desfazer"] + leis},
  {"expressao": "(A|B)&(A|C)", "acoes": (leis + ["pular"]) * 3 + ["desfazer"] + leis + ["pular", "desfazer", "desfazer"] + leis},
]
def rodar(cmd, dados):
    shutil.rmtree(dados, ignore_errors=True); os.makedirs(dados)
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=300).stdout
    return json.loads(out.split("@@JSON@@")[1])
total = 0
for r in roteiros:
    arg = json.dumps(r)
    desk = rodar(XVFB + [PY_DESKTOP, f"{N}/desktop_original.py", arg, f"{TMP}/desk"], f"{TMP}/desk")
    web = rodar([sys.executable, f"{N}/web_mesmo_roteiro.py", arg, f"{TMP}/web"], f"{TMP}/web")
    difs = [(i, a["acao"], k) for i, (a, b) in enumerate(zip(desk, web)) for k in ("estado", "popups") if a[k] != b[k]]
    total += len(difs)
    passos = sum(1 for p in desk if p["popups"] == [] and p["acao"] not in ("iniciar",))
    print(f"{r['expressao']:>14}: {len(desk)} ações comparadas, {len(difs)} diferenças; final desktop={desk[-1]['estado']['expressao']!r} web={web[-1]['estado']['expressao']!r}; cartões={len(desk[-1]['estado']['cartoes'])}")
    for i, acao, k in difs[:3]:
        print("   DIF", i, acao, k, "\n     desk:", json.dumps(desk[i][k], ensure_ascii=False)[:400], "\n     web :", json.dumps(web[i][k], ensure_ascii=False)[:400])
print("TOTAL DE DIFERENÇAS:", total)
sys.exit(1 if total else 0)

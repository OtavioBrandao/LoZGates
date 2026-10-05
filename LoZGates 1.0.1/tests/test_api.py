"""API web: entrada -> JSON esperado, para cada funcionalidade (e os erros)."""
from tests.paridade import sessao_de_uso


def erro(resposta):
    return resposta.json()["erro"]


def test_saude(cliente):
    assert cliente.get("/api/saude").json() == {"status": "ok", "versao": "1.0.1"}


# ------------------------------ expressão ------------------------------

def test_converter(cliente):
    resposta = cliente.post("/api/expressao/converter", json={"expressao": "A&B>C"})
    assert resposta.status_code == 200
    assert resposta.json() == {"expressao": "A&B>C", "expressao_booleana": "~(A*B)+C", "variaveis": ["A", "B", "C"]}


def test_expressao_invalida_tem_mensagem_e_posicao(cliente):
    resposta = cliente.post("/api/expressao/converter", json={"expressao": "AB"})
    assert resposta.status_code == 422
    assert erro(resposta)["tipo"] == "expressao_invalida"
    assert erro(resposta)["posicao"] == 1
    assert "Falta um operador entre 'A' e 'B'" in erro(resposta)["mensagem"]


def test_expressao_vazia(cliente):
    resposta = cliente.post("/api/expressao/converter", json={"expressao": "   "})
    assert resposta.status_code == 422
    assert erro(resposta) == {"tipo": "requisicao_invalida", "mensagem": "expressao: Value error, A expressão não pode estar vazia."}


def test_tabela_verdade(cliente):
    dados = cliente.post("/api/expressao/tabela-verdade", json={"expressao": "A*B"}).json()
    assert dados["colunas"] == ["A", "B", "A*B"]
    assert dados["resultados_finais"] == [0, 0, 0, 1]
    assert dados["conclusao"] == "A expressão é SATISFATÍVEL."
    assert dados["tipo_conclusao"] == "satisfativel"
    tautologia = cliente.post("/api/expressao/tabela-verdade", json={"expressao": "A|!A"}).json()
    assert tautologia["tipo_conclusao"] == "tautologia"


def test_limite_de_variaveis(cliente):
    resposta = cliente.post("/api/expressao/tabela-verdade", json={"expressao": "&".join("ABCDEFGHIJKLM")})
    assert resposta.status_code == 422 and erro(resposta)["tipo"] == "limite_excedido"
    assert "13 variáveis" in erro(resposta)["mensagem"]


# ------------------------------ simplificações ------------------------------

def test_simplificacao_automatica(cliente):
    dados = cliente.post("/api/simplificacao/automatica", json={"expressao": "(A&1)|(B&!B)"}).json()
    assert dados["expressao_final"] == "A"
    assert [p["lei"] for p in dados["passos"]] == ["Identidade", "Inversa", "Identidade"]
    primeiro = dados["passos"][0]
    inicio, fim = primeiro["trecho_antes"]
    assert primeiro["expressao_antes"][inicio:fim] == primeiro["subexpressao_antes"] == "(A&1)"


def test_simplificacao_interativa_completa(cliente):
    leis = cliente.get("/api/simplificacao/interativa/leis").json()
    assert len(leis) == 9 and leis[2] == {"indice": 2, "nome": "Identidade (A * 1 = A)"}
    inicio = cliente.post("/api/simplificacao/interativa/iniciar", json={"expressao": "(A&1)|C"}).json()
    assert inicio["visao"]["subexpressao"] == "(A*1)"
    aplicada = cliente.post("/api/simplificacao/interativa/aplicar", json={"estado": inicio["estado"], "lei": 2}).json()
    assert aplicada["visao"]["expressao"] == "(A+C)"
    assert [e["metodo"] for e in aplicada["eventos"]] == ["log_law_applied"]
    aviso = cliente.post("/api/simplificacao/interativa/aplicar", json={"estado": aplicada["estado"], "lei": 0}).json()
    assert aviso["mensagem"] == "Esta lei não pode ser aplicada à subexpressão atual."
    pulou = cliente.post("/api/simplificacao/interativa/pular", json={"estado": aplicada["estado"]}).json()
    assert pulou["visao"]["concluida"] is True
    voltou = cliente.post("/api/simplificacao/interativa/desfazer", json={"estado": pulou["estado"]}).json()
    assert voltou["visao"]["subexpressao"] == "(A+C)"


def test_estado_interativo_corrompido(cliente):
    resposta = cliente.post("/api/simplificacao/interativa/pular", json={"estado": {"versao": 1}})
    assert resposta.status_code == 422 and erro(resposta)["tipo"] == "estado_invalido"


# ------------------------------ equivalência ------------------------------

def test_equivalencia(cliente):
    assert cliente.post("/api/equivalencia", json={"expressao1": "P>Q", "expressao2": "!P|Q"}).json()["equivalentes"]
    dados = cliente.post("/api/equivalencia", json={"expressao1": "A&B", "expressao2": "X&Y"}).json()
    assert dados["equivalentes"] is False
    assert dados["contraexemplo"] == {"A": False, "B": False, "X": True, "Y": True}


def test_equivalencia_vazia(cliente):
    resposta = cliente.post("/api/equivalencia", json={"expressao1": "A", "expressao2": " "})
    assert resposta.status_code == 422 and "não podem estar vazias" in erro(resposta)["mensagem"]


# ------------------------------ problemas ------------------------------

def test_problemas(cliente):
    lista = cliente.get("/api/problemas").json()
    assert lista[0] == {"indice": 0, "nome": "Airbags", "dificuldade": "Fácil"}
    detalhe = cliente.get("/api/problemas/0").json()
    assert detalhe["resposta"] == "(V & P & I)"
    certa = cliente.post("/api/problemas/0/verificar", json={"resposta": "I&P&V"}).json()
    assert certa == {"correta": True, "mensagem": "✅ Resposta correta! Parabéns!", "tipo": "equivalente"}
    assert cliente.get("/api/problemas/999").status_code == 404


# ------------------------------ circuito ------------------------------

NETLIST_E = {
    "componentes": [
        {"id": "var-A", "tipo": "variable", "nome": "A"}, {"id": "var-B", "tipo": "variable", "nome": "B"},
        {"id": "saida", "tipo": "output"}, {"id": "g1", "tipo": "and"},
    ],
    "fios": [
        {"origem": "var-A", "destino": "g1", "entrada": 0}, {"origem": "var-B", "destino": "g1", "entrada": 1},
        {"origem": "g1", "destino": "saida", "entrada": 0},
    ],
}


def test_layout_do_circuito(cliente):
    dados = cliente.post("/api/circuito/layout", json={"expressao": "A&B", "valores": {"A": True, "B": True}}).json()
    assert dados["portas"][0]["tipo"] == "AND" and dados["valor"] is True
    assert dados["saida"]["de"] == [610, 190]


def test_modos_componentes_e_editor(cliente):
    modos = cliente.get("/api/circuito/modos").json()
    assert [m["chave"] for m in modos] == ["livre", "basic_gates", "nand_only", "nor_only", "advanced_gates", "minimal"]
    assert modos[2]["restrictions"] == ["nand"] and modos[2]["dicas"]
    assert cliente.get("/api/circuito/componentes").json()["tipos"]["not"]["saida"] == [46, 40]
    editor = cliente.post("/api/circuito/editor", json={"expressao": "A>B"}).json()
    assert editor["expressao_booleana"] == "~A+B"
    assert [c["id"] for c in editor["componentes"]] == ["var-A", "var-B", "saida"]


def test_validar_e_simular(cliente):
    validacao = cliente.post("/api/circuito/validar", json={"expressao": "A&B", "modo": "livre", "netlist": NETLIST_E}).json()
    assert validacao["correto"] is True and validacao["motivo"] == "correto"
    proibido = cliente.post("/api/circuito/validar", json={"expressao": "A&B", "modo": "nor_only", "netlist": NETLIST_E}).json()
    assert proibido["motivo"] == "porta_nao_permitida"
    saidas = cliente.post("/api/circuito/simular", json={"netlist": NETLIST_E, "valores": {"A": True, "B": False}}).json()
    assert saidas["saidas"]["g1"] is False


def test_netlist_malformada(cliente):
    netlist = {"componentes": [{"id": "x", "tipo": "and"}], "fios": [{"origem": "x", "destino": "x", "entrada": 0}]}
    resposta = cliente.post("/api/circuito/validar", json={"expressao": "A", "netlist": netlist})
    assert resposta.status_code == 422 and erro(resposta)["tipo"] == "circuito_invalido"


# ------------------------------ IA ------------------------------

def test_ia(cliente, assistente):
    assert cliente.get("/api/ia/estado").json() == {"configurada": True}
    sugestao = cliente.post("/api/ia/sugestao", json={"expressao": "A*1", "contexto": "Analisando subexpressão: (A*1)"}).json()
    assert sugestao["resposta"].startswith("Lei:")
    pergunta = cliente.post("/api/ia/pergunta", json={"pergunta": "O que é AND?", "expressao": "A*B"}).json()
    assert pergunta == {"resposta": "Resposta para: O que é AND?"}
    assert assistente.pedidos[0] == ("sugestao", "A*1", "Analisando subexpressão: (A*1)")


def test_ia_sem_chave(cliente, assistente):
    assistente.configured = False
    resposta = cliente.post("/api/ia/sugestao", json={"expressao": "A"})
    assert resposta.status_code == 503 and erro(resposta)["tipo"] == "ia_nao_configurada"


# ------------------------------ registro de uso ------------------------------

def test_telemetria(cliente, enviador):
    dados = sessao_de_uso.como_dados()
    resumo = cliente.post("/api/telemetria/resumo", json=dados).json()
    assert resumo["sessao"]["user_id"] == "aluno-123"
    assert "SIMPLIFICAÇÃO INTERATIVA" in resumo["previa"]
    assert cliente.post("/api/telemetria/enviar", json=dados).json() == {"enviado": True}
    (enviado,) = enviador.envios
    assert set(enviado) >= {"app_version", "platform", "submission_date", "summary_json"}


def test_telemetria_invalida(cliente):
    dados = {**sessao_de_uso.como_dados(), "chamadas": [{"metodo": "os.system", "argumentos": [], "momento": 1}]}
    resposta = cliente.post("/api/telemetria/resumo", json=dados)
    assert resposta.status_code == 422 and erro(resposta)["tipo"] == "telemetria_invalida"


def test_conteudo(cliente):
    dados = cliente.get("/api/conteudo").json()
    assert "LoZ Gates" in dados["boas_vindas"]
    assert set(dados["exemplos"]) == {"basic", "intermediate", "advanced"}

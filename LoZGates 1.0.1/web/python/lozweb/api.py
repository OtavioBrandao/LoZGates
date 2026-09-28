"""
Funções que o React chama. Cada uma corresponde a um callback de FrontEnd/interface.py
(ou das outras telas do desktop) e chama exatamente as mesmas funções do BackEnd, na
mesma ordem, com as mesmas mensagens e os mesmos registros no DetailedUserLogger.

Todas recebem tipos simples e devolvem uma string JSON:
    {"ok": true, ...}                    sucesso
    {"ok": false, "popup": "mensagem"}   o desktop mostraria popup_erro(mensagem)
    {"ok": false, "excecao": "..."}      exceção não tratada (no desktop: traceback no
                                         terminal e nada na tela)
"""

import base64
import functools
import io
import json
import os
import sys
import textwrap
import time
import traceback

from . import interativo, passos, plataforma, rede, tkweb

# --------------------------------------------------------------------------
# Estado global (espelha as globais de interface.py)
# --------------------------------------------------------------------------
user_logger = None
expressao_global = ""
_sessao_interativa = None
_gerenciador_circuito = None
_quadro_circuito = None
_ponte_js = None
_assistente_ia = None
_chave_ia = None
_sessao_encerrada = False
_dados_compartilhamento = None

# Mesmos valores de interface.on_closing()
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd9QNzL1_1MpD0cy_PUA4b59Kpy998015HIsfIT60VC6nOHZA/formResponse"
ENTRY_MAPPING = {
    "app_version": "entry.695751574",
    "platform": "entry.2115172041",
    "submission_date": "entry.1953189469",
    "summary_json": "entry.415910834",
}

# Nomes das abas exatamente como no CTkTabview do desktop (os logs usam esses textos)
ABA_CIRCUITO = "      Circuito      "
ABA_CIRCUITO_INTERATIVO = "  Circuito Interativo  "
ABA_EXPRESSAO = "      Expressão      "


def _json(obj):
    return json.dumps(obj, ensure_ascii=False, default=str)


def _popup(mensagem, **extra):
    return {"ok": False, "popup": mensagem, **extra}


def endpoint(funcao):
    @functools.wraps(funcao)
    def envolvida(*args, **kwargs):
        try:
            resultado = funcao(*args, **kwargs)
        except Exception as e:
            print(f"Exception in callback {funcao.__name__}", file=sys.stderr)
            traceback.print_exc()
            resultado = {"ok": False, "excecao": f"{type(e).__name__}: {e}", "mensagem": str(e)}
        if resultado is None:
            resultado = {"ok": True}
        return _json(resultado)

    return envolvida


# --------------------------------------------------------------------------
# Inicialização
# --------------------------------------------------------------------------
@endpoint
def iniciar(chave_ia=""):
    global user_logger, _chave_ia
    plataforma.preparar()
    from FrontEnd.logging_system import DetailedUserLogger

    # interface.py: user_logger = DetailedUserLogger("1.0-beta")
    user_logger = DetailedUserLogger("1.0-beta")
    _chave_ia = chave_ia or None
    return {"ok": True, "arquivos": [user_logger.log_file, user_logger.settings_file]}


@endpoint
def textos():
    """Textos que o desktop lê de config.py e de CircuitModeManager."""
    import config
    from BackEnd.circuito_logico.circuit_mode_selector import CircuitModeManager

    gerenciador = CircuitModeManager()
    modos = [{"chave": chave, **info} for chave, info in gerenciador.get_all_modes().items()]
    dicas = {m["chave"]: gerenciador.get_mode_tips(m["chave"]) for m in modos}
    return {
        "duvida_circuitos": config.duvida_circuitos,
        "welcome_message": config.welcome_message,
        "modos": modos,
        "dicas_modos": dicas,
    }


# --------------------------------------------------------------------------
# Tela "Circuitos e Expressões" (principal)
# --------------------------------------------------------------------------
@endpoint
def confirmar_expressao(texto):
    expressao_texto = texto.strip()
    if not expressao_texto:
        user_logger.log_expression_entered("", False)
        return _popup("A expressão não pode estar vazia.")

    # LOG DA EXPRESSÃO INSERIDA
    user_logger.log_expression_entered(expressao_texto.upper().replace(" ", ""), True)
    return {"ok": True}


def _ver_circuito_pygame(expressao):
    """ver_circuito_pygame() + aguardar_imagem() + atualizar_imagem_circuito() do desktop."""
    import BackEnd.principal as circuito_integrado
    from config import ASSETS_PATH
    from PIL import Image, ImageOps

    caminho_imagem = os.path.join(ASSETS_PATH, "circuito.png")
    if os.path.exists(caminho_imagem):
        try:
            os.remove(caminho_imagem)
        except Exception as e:
            print(f"Aviso: Não foi possível remover imagem anterior: {e}")

    popup = None
    try:
        circuito_integrado.plotar_circuito_logico(expressao, 0, 1200, 800)
        print("Circuito gerado com sucesso!")
    except Exception as e:
        print(f"Erro ao gerar circuito: {e}")
        popup = f"Erro ao gerar circuito: {e}"

    if not os.path.exists(caminho_imagem):
        return {"imagem": None, "imagem_original": None,
                "popup": popup or "Erro: A imagem do circuito não foi criada a tempo."}

    try:
        imagem_pil = Image.open(caminho_imagem)
        # Adiciona borda branca de 10px
        borda = 10
        imagem_com_borda = ImageOps.expand(imagem_pil, border=borda, fill="white")
        buffer = io.BytesIO()
        imagem_com_borda.save(buffer, format="PNG")
        with open(caminho_imagem, "rb") as arquivo:
            original = arquivo.read()
        return {
            "imagem": base64.b64encode(buffer.getvalue()).decode("ascii"),
            "imagem_original": base64.b64encode(original).decode("ascii"),
            "largura": imagem_com_borda.width,
            "altura": imagem_com_borda.height,
            "popup": popup,
        }
    except Exception as e:
        print(f"Erro ao atualizar imagem: {e}")
        return {"imagem": None, "imagem_original": None, "texto_imagem": f"Erro ao carregar imagem: {e}", "popup": popup}


@endpoint
def trocar_para_abas(texto):
    global expressao_global
    from BackEnd.converter import converter_para_algebra_booleana
    from config import ASSETS_PATH

    try:
        caminho_entrada = os.path.join(ASSETS_PATH, "entrada.txt")
        start_time = time.time()
        expressao = texto.strip().upper().replace(" ", "")

        user_logger.log_expression_entered(expressao, bool(expressao))

        if not expressao:
            user_logger.log_error("validation_error", "Empty expression")
            return _popup("A expressão não pode estar vazia.")

        label = f"Expressão Lógica Proposicional: {expressao}"

        os.makedirs(ASSETS_PATH, exist_ok=True)
        with open(caminho_entrada, "w", encoding="utf-8") as file:
            file.write(expressao)

        saida = converter_para_algebra_booleana(expressao)
        expressao_global = saida

        # No desktop o circuito é gerado numa thread e a tela troca imediatamente;
        # a duração registrada não inclui a geração da imagem.
        duration = time.time() - start_time
        imagem = _ver_circuito_pygame(saida)
        user_logger.log_feature_used("circuit_generation", duration)

        return {"ok": True, "label": label, "expressao_global": saida, **imagem}
    except Exception as e:
        print(f"Erro detalhado: {e}")
        return _popup(f"Erro ao processar expressão: {e}")


# --------------------------------------------------------------------------
# Abas
# --------------------------------------------------------------------------
@endpoint
def mudar_aba(nome_aba):
    """on_tab_change(): registra a navegação."""
    user_logger.log_tab_changed("tab_navigation", nome_aba)
    return {"ok": True}


@endpoint
def expressao_convertida(texto):
    """mostrar_expressao_convertida()"""
    from BackEnd.converter import converter_para_algebra_booleana

    try:
        entrada_txt = texto.strip().upper()
        if not entrada_txt:
            return _popup("Digite uma expressão primeiro.")
        saida_booleana = converter_para_algebra_booleana(entrada_txt)
        return {
            "ok": True,
            "expressao_booleana": saida_booleana,
            "texto": f"Expressão em Álgebra Booleana: {saida_booleana}",
        }
    except Exception as e:
        return _popup(f"Erro ao converter expressão: {e}")


@endpoint
def tabela_verdade(expressao):
    """exibir_tabela_verdade()"""
    from BackEnd.tabela import gerar_tabela_verdade, verificar_conclusao

    try:
        dados_tabela = gerar_tabela_verdade(expressao)
        colunas = dados_tabela["colunas"]
        tabela = dados_tabela["tabela"]
        resultados_finais = dados_tabela["resultados_finais"]

        conclusao = verificar_conclusao(resultados_finais)
        if "TAUTOLOGIA" in conclusao:
            cor_conclusao = "sucesso"   # Colors.SUCCESS
        elif "CONTRADIÇÃO" in conclusao:
            cor_conclusao = "erro"      # Colors.ERROR
        else:
            cor_conclusao = "info"      # Colors.INFO

        return {
            "ok": True,
            "titulo": f"Tabela Verdade: {expressao}",
            "colunas": [str(c) for c in colunas],
            "tabela": tabela,
            "conclusao": conclusao,
            "cor_conclusao": cor_conclusao,
        }
    except Exception as e:
        print(f"Erro detalhado: {e}")
        return _popup(f"Erro ao gerar tabela verdade: {e}")


# --------------------------------------------------------------------------
# Simplificar - Resultado
# --------------------------------------------------------------------------
@endpoint
def simplificar_resultado(texto):
    """expressao_simplificada()"""
    from BackEnd.converter import converter_para_algebra_booleana

    try:
        entrada_txt = texto.strip().upper()
        if not entrada_txt:
            return _popup("A expressão na tela principal está vazia.")

        expressao_para_simplificar = converter_para_algebra_booleana(entrada_txt)
        resultado = passos.executar_simplificacao(expressao_para_simplificar)
        resultado["ok"] = True
        if resultado.get("erro"):
            resultado["popup"] = resultado["erro"]
        return resultado
    except Exception as e:
        return _popup(f"Erro ao simplificar expressão: {e}")


# --------------------------------------------------------------------------
# Simplificar - Interativo
# --------------------------------------------------------------------------
def _estado_interativo(extra=None):
    estado = _sessao_interativa.estado()
    return {"ok": True, "estado": estado, "popups": estado.pop("popups"), **(extra or {})}


@endpoint
def interativo_iniciar():
    """parte_interativa()"""
    global _sessao_interativa
    _sessao_interativa = interativo.SimplificacaoInterativa(user_logger)
    falha = _sessao_interativa.parte_interativa(expressao_global)
    if falha:
        return {"ok": False, **falha}
    return _estado_interativo()


@endpoint
def interativo_lei(indice_lei):
    _sessao_interativa.on_lei_selecionada(int(indice_lei))
    return _estado_interativo()


@endpoint
def interativo_pular():
    _sessao_interativa.on_pular_selecionado()
    return _estado_interativo()


@endpoint
def interativo_desfazer():
    _sessao_interativa.on_desfazer_selecionado()
    return _estado_interativo()


@endpoint
def interativo_contexto_ia():
    if _sessao_interativa is None:
        return {"ok": True, "expressao": expressao_global, "contexto": ""}
    expressao, contexto = _sessao_interativa.contexto_ia(expressao_global)
    return {"ok": True, "expressao": expressao, "contexto": contexto}


# --------------------------------------------------------------------------
# Equivalência Lógica
# --------------------------------------------------------------------------
@endpoint
def comparar(texto1, texto2):
    """comparar() do frame de equivalência."""
    try:
        expressao2 = texto1.strip().upper()
        expressao3 = texto2.strip().upper()

        if not expressao2 or not expressao3:
            return _popup("As expressões não podem estar vazias.")

        print(f"\n{'='*60}")
        print(f"🔍 COMPARAÇÃO DE EXPRESSÕES")
        print(f"{'='*60}")
        print(f"📝 Expressão 1: {expressao2}")
        print(f"📝 Expressão 2: {expressao3}")

        # PRIMEIRA VERIFICAÇÃO: Equivalência lógica direta
        print(f"\n🧮 Verificando equivalência lógica direta...")
        from BackEnd.equivalencia import check_universal_equivalence
        is_logically_equivalent = check_universal_equivalence(expressao2, expressao3, debug=True)

        if is_logically_equivalent:
            print(f"✅ RESULTADO: Expressões são logicamente equivalentes!")
            print(f"{'='*60}\n")
            resultado = True
        else:
            # SEGUNDA VERIFICAÇÃO: Equivalência estrutural (variáveis diferentes)
            print(f"\n🔄 Verificando equivalência estrutural (ignorando nomes de variáveis)...")
            from BackEnd.normalizer import normalize_for_comparison, expressions_are_structurally_equivalent

            is_structurally_equivalent = expressions_are_structurally_equivalent(expressao2, expressao3)

            if is_structurally_equivalent:
                norm1 = normalize_for_comparison(expressao2)
                norm2 = normalize_for_comparison(expressao3)

                print(f"   Expressão 1 normalizada: {norm1}")
                print(f"   Expressão 2 normalizada: {norm2}")

                is_equiv_normalized = check_universal_equivalence(norm1, norm2, debug=False)

                if is_equiv_normalized:
                    print(f"✅ RESULTADO: Expressões são estruturalmente equivalentes!")
                    print(f"{'='*60}\n")
                    resultado = True
                else:
                    print(f"❌ RESULTADO: Expressões NÃO são equivalentes")
                    print(f"{'='*60}\n")
                    resultado = False
            else:
                print(f"❌ RESULTADO: Expressões NÃO são equivalentes")
                print(f"{'='*60}\n")
                resultado = False

        # LOG DETALHADO COM EXPRESSÕES REAIS
        user_logger.log_equivalence_check_with_expressions(expressao2, expressao3, resultado)
        return {"ok": True, "equivalente": resultado}
    except Exception as e:
        user_logger.log_error("equivalence_check_error", str(e), "comparar_function")
        return _popup(f"Erro ao comparar expressões: {e}")


# --------------------------------------------------------------------------
# Banco de problemas
# --------------------------------------------------------------------------
_interface_problemas = None


def _problemas():
    global _interface_problemas
    from FrontEnd.problems_interface import IntegratedProblemsInterface

    if _interface_problemas is None:
        # O __init__ só guarda referências (nenhum widget é criado).
        _interface_problemas = IntegratedProblemsInterface(None)
    return _interface_problemas


@endpoint
def problemas_lista():
    from BackEnd.problems_bank import Problems_bank

    return {
        "ok": True,
        "problemas": [
            {"indice": i, "nome": p.name, "dificuldade": getattr(p, "difficulty", "Fácil")}
            for i, p in enumerate(Problems_bank)
        ],
    }


@endpoint
def problema_detalhe(indice):
    from BackEnd.problems_bank import Problems_bank

    p = Problems_bank[int(indice)]
    return {
        "ok": True,
        "nome": p.name,
        "dificuldade": p.difficulty,
        # O texto é o mesmo do desktop; só removemos a indentação do código-fonte.
        "pergunta": textwrap.dedent(p.question).strip("\n"),
        "resposta": p.answer,
    }


@endpoint
def problema_verificar(indice, resposta):
    from BackEnd.problems_bank import Problems_bank

    user_answer = resposta.strip()
    if not user_answer:
        return {"ok": True, "vazio": True}

    interface = _problemas()
    is_correct, message = interface.validate_answer_with_equivalence(user_answer, Problems_bank[int(indice)].answer)
    if is_correct and hasattr(interface, "user_logger"):
        interface.user_logger.log_feature_used("problem_solved", 0)
    return {"ok": True, "correta": bool(is_correct), "mensagem": message}


@endpoint
def problema_analisar():
    """handle_problem_answer(): registro antes de navegar."""
    user_logger.log_feature_used("problem_answer_analysis", 0)
    return {"ok": True}


# --------------------------------------------------------------------------
# Circuito Interativo (pygame no <canvas>)
# --------------------------------------------------------------------------
def _agendar_js(ms, funcao):
    import js
    from pyodide.ffi import create_once_callable

    return js.setTimeout(create_once_callable(funcao), ms)


def _cancelar_js(ident):
    import js

    js.clearTimeout(ident)


@endpoint
def circuito_novo_seletor(ponte):
    """create_interactive_circuit(): cria o CircuitModeManager e o "tk.Frame" do pygame."""
    global _gerenciador_circuito, _quadro_circuito, _ponte_js
    from BackEnd.circuito_logico.circuit_mode_selector import CircuitModeManager

    # LOG INÍCIO DO CIRCUITO INTERATIVO
    user_logger.log_circuit_interaction_start()

    circuito_limpar_interno()
    _ponte_js = ponte
    _gerenciador_circuito = CircuitModeManager()
    _quadro_circuito = tkweb.QuadroWeb(
        agendar=_agendar_js,
        cancelar=_cancelar_js,
        medir=lambda: tuple(ponte.medir().to_py()),
        focar=lambda: ponte.focar(),
        exibir_mensagem=lambda texto, cor: ponte.mensagem(texto, cor or ""),
    )
    return {"ok": True}


@endpoint
def circuito_selecionar_modo(chave_modo):
    _gerenciador_circuito.set_mode(chave_modo)
    return {"ok": True}


@endpoint
def circuito_iniciar(expressao, chave_modo):
    """start_circuit(): registra o modo e cria o CircuitoInterativoManual."""
    if user_logger:
        user_logger.log_event(
            "circuit_mode_selected",
            {
                "mode": chave_modo,
                "expression": expressao[:30],
                "restrictions": _gerenciador_circuito.get_mode_info(chave_modo).get("restrictions"),
            },
        )
    circuito = _gerenciador_circuito.create_circuit(_quadro_circuito, expressao, logger=user_logger)
    circuito.scroll_control_callback = lambda habilitar: _ponte_js.rolagem(bool(habilitar))
    return {"ok": True}


@endpoint
def circuito_parar():
    if _gerenciador_circuito:
        _gerenciador_circuito.stop_current_circuit()
    return {"ok": True}


def circuito_limpar_interno():
    if _gerenciador_circuito:
        _gerenciador_circuito.stop_current_circuit()


@endpoint
def circuito_limpar():
    """cleanup() do CircuitModeSelector (ao sair das abas)."""
    circuito_limpar_interno()
    return {"ok": True}


def circuito_tecla(tipo, tecla, ctrl=False, shift=False, alt=False):
    """Teclado -> bind('<KeyPress>'/'<KeyRelease>') do código original. Sem JSON (chamado a cada tecla)."""
    if _quadro_circuito is not None:
        _quadro_circuito.disparar_tecla(tipo, tecla, bool(ctrl), bool(shift), bool(alt))


def circuito_mouse_entrou():
    """bind('<Enter>') do código original (dá foco ao canvas)."""
    if _quadro_circuito is not None:
        _quadro_circuito.disparar("<Enter>")


@endpoint
def registrar_evento(tipo, dados_json="{}"):
    """logger.log_event(...) chamado pela tela (ex.: 'circuit_tips_viewed')."""
    if user_logger:
        user_logger.log_event(tipo, json.loads(dados_json or "{}"))
    return {"ok": True}


# --------------------------------------------------------------------------
# Assistente de IA (BackEnd/ai_assistant.py)
# --------------------------------------------------------------------------
def _assistente():
    global _assistente_ia
    if _assistente_ia is None:
        import BackEnd.ai_assistant as modulo_ia

        # Sem threads no navegador: start() executa direto; a espera assíncrona fica com o fetch().
        modulo_ia.threading = rede.threading_sincrono
        _assistente_ia = modulo_ia.AIAssistant()
        if _chave_ia:
            _assistente_ia.headers["Authorization"] = f"Bearer {_chave_ia}"
    return _assistente_ia


@endpoint
def ia(tipo, expressao, contexto="", pergunta="", resposta_json=None):
    """
    tipo = 'sugestao' (get_ai_suggestion) ou 'pergunta' (ask_question).
    Sem resposta_json: fase de captura (devolve o pedido HTTP para o fetch()).
    Com resposta_json: fase de resposta (devolve o que o callback original recebeu).
    """
    assistente = _assistente()
    resultados = []

    def callback(response, error):
        resultados.append({"resposta": response, "erro": error})

    if tipo == "sugestao":
        executar = lambda: assistente.get_ai_suggestion(expressao, contexto, callback)
    else:
        executar = lambda: assistente.ask_question(pergunta, expressao, callback)

    if resposta_json is None:
        pedido = rede.capturar(executar)
        return {"ok": True, "pedido": pedido, "resultados": resultados}

    rede.responder(executar, json.loads(resposta_json))
    return {"ok": True, "resultados": resultados}


# --------------------------------------------------------------------------
# Encerramento da sessão (on_closing) e compartilhamento de dados
# --------------------------------------------------------------------------
@endpoint
def encerrar_sessao():
    """on_closing(): finaliza a sessão e decide se mostra o diálogo de compartilhamento."""
    global _sessao_encerrada
    circuito_limpar_interno()
    if not _sessao_encerrada:
        user_logger.end_session()
        _sessao_encerrada = True

    if user_logger.should_prompt_data_sharing():
        from FrontEnd.logging_system import DetailedDataSharingDialog

        dialogo = DetailedDataSharingDialog(user_logger)
        summary = user_logger.get_detailed_summary()
        preview = dialogo._create_data_preview(summary) if summary else ""
        return {"ok": True, "mostrar_dialogo": True, "preview": preview}
    return {"ok": True, "mostrar_dialogo": False}


@endpoint
def encerrar_sessao_silenciosa():
    """A aba do navegador foi fechada sem passar por 'Encerrar sessão'."""
    global _sessao_encerrada
    if user_logger and not _sessao_encerrada:
        user_logger.end_session()
        _sessao_encerrada = True
    return {"ok": True}


@endpoint
def compartilhar_dados(resposta_json=None):
    """Botão '✅ Enviar Dados Detalhados' (result == True em on_closing)."""
    global _dados_compartilhamento
    from FrontEnd.logging_system import DetailedUserLogger, ImprovedGoogleFormsSubmitter

    submitter = ImprovedGoogleFormsSubmitter(FORM_URL, ENTRY_MAPPING)

    if resposta_json is None:
        print("Usuário aceitou enviar os dados detalhados. Preparando para envio...")
        _dados_compartilhamento = DetailedUserLogger.create_formatted_shareable_data(user_logger)
        dados = _dados_compartilhamento
        pedido = rede.capturar(lambda: submitter.submit_data(dados))
        return {"ok": True, "pedido": pedido}

    dados = _dados_compartilhamento or {}
    success = rede.responder(lambda: submitter.submit_data(dados), json.loads(resposta_json))
    if success:
        user_logger._save_settings()
    else:
        print("O envio falhou. Os dados não foram enviados.")
    return {"ok": True, "enviado": bool(success)}


@endpoint
def nunca_perguntar():
    """Botão '🚫 Nunca Perguntar' (result == 'never')."""
    user_logger.logging_enabled = False
    user_logger._save_settings()
    return {"ok": True}

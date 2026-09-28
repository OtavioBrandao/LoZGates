"""
Modo "Simplificar - Interativo".

No desktop essa lógica fica DENTRO de FrontEnd/interface.py, em funções aninhadas
que misturam estado global com widgets do Tk (parte_interativa, on_lei_selecionada,
on_pular_selecionado, on_desfazer_selecionado, reconstruir_area_passos...). Como
não dá para importá-las sem criar a janela Tk, elas foram transcritas aqui LINHA A
LINHA, na mesma ordem, com as mesmas mensagens, o mesmo histórico e as mesmas
chamadas ao logger. A única diferença: onde o desktop criava/alterava widgets, aqui
guardamos o equivalente em dados (self.cartoes, self.analise, estado dos botões) para
o React desenhar.

Observação: comportamentos conhecidos do desktop foram mantidos de propósito
(ex.: o contador de passos depois de "Desfazer" — ver TODO.md, "inconsistências
relacionadas ao DO e UNDO"). Corrigir isso é uma mudança de lógica e deve ser feita
no código original, não aqui.
"""

import copy
import re
import time


def _simpli():
    # Import tardio: o caminho do código do LoZ Gates só entra no sys.path em plataforma.preparar()
    import BackEnd.simplificador_interativo as simpli

    return simpli

# Cores usadas pelo desktop (design_tokens.Colors) -> nomes semânticos para o CSS
COR_PRIMARIA = "texto-primario"      # Colors.TEXT_PRIMARY
COR_SECUNDARIA = "texto-secundario"  # Colors.TEXT_SECONDARY
COR_SUCESSO = "sucesso"              # Colors.SUCCESS


class SimplificacaoInterativa:
    def __init__(self, user_logger):
        self.user_logger = user_logger

        # --- globais do interface.py ---
        self.arvore_interativa = None
        self.passo_atual_info = None
        self.nos_ignorados = set()
        self.historico_interativo = []
        self.historico_de_estados = []
        self.contador_passos = 0
        self.simplification_start_time = None

        # --- "widgets" ---
        self.cartoes = []  # conteúdo de scroll_passos
        self.label_expressao_inicial = ""
        self.label_analise = {"texto": "Aguardando início da análise...", "cor": COR_SECUNDARIA}
        self.leis_habilitadas = True
        self.pular_habilitado = True
        self.desfazer_habilitado = False
        self.popups = []

    # ------------------------------------------------------------------
    # Estado para o React
    # ------------------------------------------------------------------
    def estado(self):
        popups, self.popups = self.popups, []
        return {
            "expressao": self.label_expressao_inicial,
            "analise": dict(self.label_analise),
            "cartoes": list(self.cartoes),
            "leis_habilitadas": self.leis_habilitadas,
            "pular_habilitado": self.pular_habilitado,
            "desfazer_habilitado": self.desfazer_habilitado,
            "popups": popups,
        }

    def popup_erro(self, mensagem):
        self.popups.append(mensagem)

    # ------------------------------------------------------------------
    # parte_interativa()
    # ------------------------------------------------------------------
    def parte_interativa(self, expressao_global):
        """Devolve None se iniciou; ou {'popup':..., 'destino':...} se não pôde iniciar."""
        if not expressao_global:
            return {"popup": "Por favor, primeiro insira e converta uma expressão.", "destino": "principal"}

        try:
            self.simplification_start_time = time.time()

            # LOG INÍCIO DA SESSÃO INTERATIVA
            self.user_logger.log_interactive_simplification_start(expressao_global)

            self.arvore_interativa = _simpli().construir_arvore(expressao_global)
        except Exception as e:
            return {"popup": f"Erro ao construir a expressão: {e}", "destino": "abas"}

        self.historico_interativo = [f"Expressão Inicial: {str(self.arvore_interativa)}"]
        self.nos_ignorados = set()
        self.passo_atual_info = None
        self.historico_de_estados = []

        self.criar_interface_interativa_padronizada()
        self.inicializar_area_passos()
        self.iniciar_rodada_interativa()
        duration = time.time() - self.simplification_start_time
        self.user_logger.log_feature_used("interactive_mode", duration)
        return None

    def criar_interface_interativa_padronizada(self):
        self.cartoes = []
        self.label_expressao_inicial = ""
        self.label_analise = {"texto": "Aguardando início da análise...", "cor": COR_SECUNDARIA}
        self.leis_habilitadas = True
        self.pular_habilitado = True
        self.desfazer_habilitado = False  # botao_desfazer começa com state="disabled"

    # ------------------------------------------------------------------
    # Estados / desfazer
    # ------------------------------------------------------------------
    def salvar_estado_atual(self):
        estado = {
            "arvore": copy.deepcopy(self.arvore_interativa),
            "historico": list(self.historico_interativo),
            "ignorados": set(self.nos_ignorados),
            "passo_info": copy.deepcopy(self.passo_atual_info),
        }
        self.historico_de_estados.append(estado)

    def on_desfazer_selecionado(self):
        if not self.historico_de_estados:
            print("Nada para desfazer.")
            return

        # LOG DO UNDO
        self.user_logger.log_simplification_undo()

        estado_anterior = self.historico_de_estados.pop()
        self.arvore_interativa = estado_anterior["arvore"]
        self.historico_interativo = estado_anterior["historico"]
        self.nos_ignorados = estado_anterior["ignorados"]
        self.passo_atual_info = estado_anterior["passo_info"]

        if self.contador_passos > 0:
            self.contador_passos -= 1

        self.reconstruir_area_passos()

        if not self.historico_de_estados:
            self.desfazer_habilitado = False
        self.atualizar_ui_interativa()

    # ------------------------------------------------------------------
    # Área de passos
    # ------------------------------------------------------------------
    def inicializar_area_passos(self):
        self.contador_passos = 0
        self.cartoes = []
        self.adicionar_passo_inicial(str(self.arvore_interativa))

    def adicionar_passo_inicial(self, expressao_inicial):
        self.cartoes.append({"tipo": "inicial", "titulo": "Estado Inicial", "expressao": expressao_inicial})

    def adicionar_passo_sucesso(self, lei_nome, subexpressao, antes, depois, resultado):
        self.contador_passos += 1
        self.cartoes.append(
            {
                "tipo": "sucesso",
                "titulo": f"Passo {self.contador_passos} — {lei_nome}",
                "subexpressao": f"Subexpressão: {subexpressao}" if subexpressao else "",
                "transformacao": f"{antes} → {depois}",
                "status": f"✔ {resultado}",
            }
        )

    def adicionar_passo_pular(self, subexpressao):
        self.cartoes.append(
            {
                "tipo": "pular",
                "titulo": "Subexpressão Ignorada",
                "texto": f"↷ '{subexpressao}' foi ignorada",
            }
        )

    def reconstruir_area_passos(self):
        self.cartoes = []

        if self.historico_interativo and len(self.historico_interativo) > 0:
            primeiro_item = self.historico_interativo[0]
            if "Expressão Inicial:" in primeiro_item:
                expressao_inicial = primeiro_item.replace("Expressão Inicial:", "").strip()
                self.adicionar_passo_inicial(expressao_inicial)

            passo_num = 0
            i = 1
            while i < len(self.historico_interativo):
                linha = self.historico_interativo[i]
                if "✓ Lei" in linha and "aplicada com sucesso" in linha:
                    passo_num += 1
                    lei_match = re.search(r"Lei '(.+?)' aplicada", linha)
                    lei_nome = lei_match.group(1) if lei_match else "Lei desconhecida"

                    if i + 1 < len(self.historico_interativo):
                        proxima_linha = self.historico_interativo[i + 1]
                        if "Nova Expressão:" in proxima_linha:
                            nova_expr = proxima_linha.replace("Nova Expressão:", "").strip()
                            self.adicionar_passo_sucesso(lei_nome, "", "(anterior)", "(simplificada)", nova_expr)
                            i += 1
                elif "↷ Sub-expressão" in linha and "ignorada" in linha:
                    ignore_match = re.search(r"'(.+?)' ignorada", linha)
                    subexpr = ignore_match.group(1) if ignore_match else "desconhecida"
                    self.adicionar_passo_pular(subexpr)
                i += 1

    # ------------------------------------------------------------------
    # Ações dos botões
    # ------------------------------------------------------------------
    def on_lei_selecionada(self, indice_lei):
        if not self.passo_atual_info:
            return

        self.salvar_estado_atual()
        self.desfazer_habilitado = True

        lei_usada = _simpli().LEIS_LOGICAS[indice_lei]["nome"]
        subexpressao_antes = str(self.passo_atual_info["no_atual"])

        nova_arvore, sucesso = _simpli().aplicar_lei_e_substituir(self.arvore_interativa, self.passo_atual_info, indice_lei)

        # LOG DA APLICAÇÃO DE LEI
        self.user_logger.log_law_applied(lei_usada, sucesso, self.contador_passos + 1)

        if sucesso:
            self.arvore_interativa = nova_arvore

            self.historico_interativo.append(f"✓ Lei '{lei_usada}' aplicada com sucesso.")
            self.historico_interativo.append(f"   Nova Expressão: {str(self.arvore_interativa)}")
            self.nos_ignorados = set()

            self.adicionar_passo_sucesso(
                lei_usada, subexpressao_antes, subexpressao_antes, "(simplificada)", str(self.arvore_interativa)
            )
            self.iniciar_rodada_interativa()
        else:
            # LOG DA FALHA
            full_expression_state = str(self.arvore_interativa)
            reason_for_failure = (
                f"Lei não aplicável à subexpressão '{subexpressao_antes}' no contexto de '{full_expression_state}'"
            )
            self.user_logger.log_simplification_step_failed(
                lei_usada, self.contador_passos + 1, reason_for_failure, full_expression_state
            )

            self.historico_de_estados.pop()
            if not self.historico_de_estados:
                self.desfazer_habilitado = False
            self.popup_erro("Não foi possível aplicar esta lei.")

    def on_pular_selecionado(self):
        if self.passo_atual_info and self.passo_atual_info["no_atual"]:
            self.salvar_estado_atual()
            self.desfazer_habilitado = True
            subexpressao_ignorada = str(self.passo_atual_info["no_atual"])

            # LOG DO PULAR
            self.user_logger.log_simplification_skip(self.contador_passos)

            self.nos_ignorados.add(self.passo_atual_info["no_atual"])
            self.historico_interativo.append(f"↷ Sub-expressão '{subexpressao_ignorada}' ignorada.")
            self.adicionar_passo_pular(subexpressao_ignorada)
            self.iniciar_rodada_interativa()

    def atualizar_ui_interativa(self):
        if self.arvore_interativa:
            self.label_expressao_inicial = str(self.arvore_interativa)

        if self.passo_atual_info:
            sub_expr = str(self.passo_atual_info["no_atual"])
            self.label_analise = {
                "texto": f"🔍 Analisando subexpressão: '{sub_expr}'\n📚 Selecione uma lei para aplicar.",
                "cor": COR_PRIMARIA,
            }
            self.leis_habilitadas = True
            self.pular_habilitado = True
        else:
            self.label_analise = {
                "texto": "✅ Simplificação concluída!\n🎉 Nenhuma outra lei pode ser aplicada.",
                "cor": COR_SUCESSO,
            }

            if self.historico_interativo:
                total_steps = self.contador_passos

                laws_used = []
                for line in self.historico_interativo:
                    if "✓ Lei" in line and "aplicada com sucesso" in line:
                        lei_match = re.search(r"Lei '(.+?)' aplicada", line)
                        if lei_match:
                            laws_used.append(lei_match.group(1))

                self.user_logger.log_simplification_completed(total_steps, laws_used)
                print(f"📝 Simplificação concluída: {total_steps} passos, {len(laws_used)} leis aplicadas")

            self.leis_habilitadas = False
            self.pular_habilitado = False

    def iniciar_rodada_interativa(self):
        self.passo_atual_info = _simpli().encontrar_proximo_passo(self.arvore_interativa, nos_a_ignorar=self.nos_ignorados)
        self.atualizar_ui_interativa()

    # ------------------------------------------------------------------
    # 🤖 Sugestão de IA (abrir_chat_ia)
    # ------------------------------------------------------------------
    def contexto_ia(self, expressao_global):
        expressao_atual = str(self.arvore_interativa) if self.arvore_interativa else expressao_global
        contexto_passo = ""
        if self.passo_atual_info:
            subexpr = str(self.passo_atual_info["no_atual"])
            contexto_passo = f"Analisando subexpressão: {subexpr}"
        return expressao_atual, contexto_passo

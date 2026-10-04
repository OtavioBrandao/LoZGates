import time
import logging

import tests.paridade.oraculo_interface_update.BackEnd.simplificador_interativo as simpli

logger = logging.getLogger(__name__)

class ResolverController:
    def __init__(self, state, user_logger, on_step_callback=None, on_skip_callback=None):
        self.state = state
        self.user_logger = user_logger
        self.view = None

    def set_view(self, view):
        self.view = view

    def iniciar_simplificacao(self, expressao_str):
        self.state.reset()
        self.state.expressao_global = expressao_str
        self.state.simplification_start_time = time.time()
        
        # Log the start of the interactive session to avoid ZeroDivisionError
        if self.user_logger:
            self.user_logger.log_interactive_simplification_start(expressao_str)
        
        arvore = simpli.construir_arvore(expressao_str)
        if not arvore:
            raise ValueError(f"Não foi possível parsear a expressão: {expressao_str}")
            
        self.state.arvore_interativa = arvore
        self.state.simplification_guard = simpli.SimplificationGuard(self.state.arvore_interativa)
        
        self.state.historico_interativo.append(f"Expressão inicial: {str(arvore)}")
        self.iniciar_rodada_interativa()

    def iniciar_rodada_interativa(self):
        self.state.passo_atual_info = simpli.encontrar_proximo_passo(
            self.state.arvore_interativa, 
            nos_a_ignorar=self.state.nos_ignorados
        )
        
        if self.state.passo_atual_info is None and self.state.motivo_parada_interativo is None:
            self.state.motivo_parada_interativo = "no_further_simplification"
            logger.info(
                "no further simplification in interactive mode: expression=%s",
                self.state.arvore_interativa,
            )
            
        if self.view:
            self.view.atualizar_ui()

    def on_lei_selecionada(self, indice_lei):
        if not self.state.passo_atual_info:
            return
            
        try:
            lei = simpli.LEIS_LOGICAS[indice_lei]
            lei_usada = lei['nome']
            no_atual = self.state.passo_atual_info['no_atual']
            subexpressao_antes = str(no_atual)
            
            # Validação Pedagógica: se não for aplicável, mostra popup
            if not lei['verifica'](no_atual):
                if self.view:
                    self.view.popup_erro("Esta lei não pode ser aplicada à subexpressão atual.")
                return

            self.state.save_snapshot()
            
            nova_arvore, sucesso = simpli.aplicar_lei_e_substituir(
                self.state.arvore_interativa, self.state.passo_atual_info, indice_lei
            )

            self.user_logger.log_law_applied(lei_usada, sucesso, self.state.contador_passos + 1)

            if sucesso:
                decision = self.state.simplification_guard.consider(nova_arvore)
                if not decision.accepted:
                    self.state.restore_snapshot()
                    self.state.motivo_parada_interativo = decision.reason
                    simpli.reiniciar_busca()
                    
                    if decision.reason == "maximum_steps":
                        logger.warning("maximum steps reached in interactive simplification")
                    elif decision.reason == "repeated_state":
                        logger.warning("repeated state detected in interactive simplification: %s", nova_arvore)
                    else:
                        logger.warning("interactive transformation stopped without progress")
                        
                    if self.view:
                        self.view.atualizar_ui()
                    return

                self.state.arvore_interativa = nova_arvore
                self.state.motivo_parada_interativo = None
                self.state.sessao_simplificacao_concluida = False
                
                self.state.contador_passos += 1

                self.state.historico_interativo.append(f"✓ Lei '{lei_usada}' aplicada com sucesso.")
                self.state.historico_interativo.append(f"   Nova Expressão: {str(self.state.arvore_interativa)}")
                self.state.nos_ignorados = set()

                logger.info(
                    "rule applied in interactive simplification: rule=%s step=%s expression=%s",
                    lei_usada,
                    self.state.contador_passos,
                    self.state.arvore_interativa,
                )
                
                if self.view:
                    self.view.adicionar_passo_sucesso(
                        lei_usada, subexpressao_antes, subexpressao_antes,
                        "(simplificada)", str(self.state.arvore_interativa)
                    )
                    
                self.iniciar_rodada_interativa()
            else:
                full_expression_state = str(self.state.arvore_interativa)
                reason_for_failure = f"Lei não aplicável à subexpressão '{subexpressao_antes}' no contexto de '{full_expression_state}'"
                self.user_logger.log_simplification_step_failed(
                    lei_usada,
                    self.state.contador_passos + 1,
                    reason_for_failure,
                    full_expression_state,
                )

                # Desfaz o snapshot já que a lei não modificou a árvore validamente
                self.state.restore_snapshot()
                
                if self.view:
                    self.view.popup_erro("Esta transformação não reduz a expressão atual.")
                self.iniciar_rodada_interativa()
                
        except Exception:
            logger.exception("simplification exception in interactive rule handler")
            if self.view:
                self.view.popup_erro("Não foi possível aplicar a lei selecionada.")
            self.iniciar_rodada_interativa()

    def on_pular_selecionado(self):
        if self.state.passo_atual_info and self.state.passo_atual_info['no_atual']:
            self.state.save_snapshot()
            
            subexpressao_ignorada = str(self.state.passo_atual_info['no_atual'])
            
            # LOG DO PULAR
            self.user_logger.log_simplification_skip(self.state.contador_passos)
            
            self.state.nos_ignorados.add(self.state.passo_atual_info['no_atual'])
            self.state.sessao_simplificacao_concluida = False
            self.state.historico_interativo.append(f"⏭ Sub-expressão '{subexpressao_ignorada}' ignorada.")
            
            if self.view:
                self.view.adicionar_passo_pular(subexpressao_ignorada)
                
            self.iniciar_rodada_interativa()

    def on_desfazer_selecionado(self):
        if not self.state.historico_de_estados:
            logger.debug("Nenhum estado de simplificacao para desfazer")
            return

        # LOG DO UNDO
        self.user_logger.log_simplification_undo()

        sucesso = self.state.restore_snapshot()
        if sucesso:
            self.state.simplification_guard = simpli.SimplificationGuard(self.state.arvore_interativa)
            simpli.reiniciar_busca()
            
            if self.view:
                self.view.reconstruir_area_passos()
                
            self.iniciar_rodada_interativa()

    def concluir_sessao(self):
        if self.state.sessao_simplificacao_concluida:
            return
            
        self.state.sessao_simplificacao_concluida = True
        elapsed_time = 0.0
        if self.state.simplification_start_time:
            elapsed_time = time.time() - self.state.simplification_start_time
            
        self.user_logger.log_simplification_completed(self.state.contador_passos, elapsed_time)

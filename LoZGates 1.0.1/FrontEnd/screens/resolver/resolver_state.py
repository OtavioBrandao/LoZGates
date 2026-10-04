import copy

class ResolverState:
    def __init__(self):
        self.arvore_interativa = None
        self.historico_interativo = []
        self.historico_de_estados = []
        self.nos_ignorados = set()
        self.contador_passos = 0
        self.passo_atual_info = None
        self.sessao_simplificacao_concluida = False
        self.motivo_parada_interativo = None
        self.simplification_guard = None
        self.simplification_start_time = None
        self.expressao_global = ""

    def reset(self):
        self.arvore_interativa = None
        self.historico_interativo = []
        self.historico_de_estados = []
        self.nos_ignorados = set()
        self.contador_passos = 0
        self.passo_atual_info = None
        self.sessao_simplificacao_concluida = False
        self.motivo_parada_interativo = None
        self.simplification_guard = None
        self.simplification_start_time = None
        self.expressao_global = ""

    def save_snapshot(self):
        """Salva um snapshot do estado atual para permitir Undo correto."""
        # nos_ignorados guarda id() dos nós; o memo do deepcopy diz qual cópia
        # corresponde a cada nó original, para os ids apontarem para a árvore copiada.
        memo = {}
        arvore_copiada = copy.deepcopy(self.arvore_interativa, memo)
        ignorados_copiados = {id(memo[i]) for i in self.nos_ignorados if i in memo}

        estado = {
            'arvore': arvore_copiada,
            'historico': list(self.historico_interativo),
            'ignorados': ignorados_copiados,
        }
        self.historico_de_estados.append(estado)

    def restore_snapshot(self):
        """Restaura o último snapshot, retornando True se houve sucesso, False se não havia histórico."""
        if not self.historico_de_estados:
            return False
            
        estado_anterior = self.historico_de_estados.pop()
        self.arvore_interativa = estado_anterior['arvore']
        self.historico_interativo = estado_anterior['historico']
        self.nos_ignorados = estado_anterior.get('ignorados', set())
        
        self.passo_atual_info = None
        self.sessao_simplificacao_concluida = False
        self.motivo_parada_interativo = None
        
        return True

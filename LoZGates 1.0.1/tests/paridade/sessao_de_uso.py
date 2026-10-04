"""Uma sessão de uso realista (chamadas ao registro com o instante de cada uma)."""

INICIO = 1_790_000_000.0
FUSO_MINUTOS = -180  # Brasília

CHAMADAS = [
    ("log_expression_entered", ["A>B", True]),
    ("log_feature_used", ["circuit_generation", 0.42]),
    ("log_tab_changed", ["tab_navigation", "  Circuito Interativo  "]),
    ("log_circuit_interaction_start", []),
    ("log_event", ["circuit_mode_selected", {"mode": "nand_only", "expression": "(~A+B)", "restrictions": ["nand"]}]),
    ("log_component_action", ["add", "nand"]),
    ("log_component_action", ["connect"]),
    ("log_component_action", ["delete", "nand"]),
    ("log_component_action", ["undo"]),
    ("log_circuit_test", [False]),
    ("log_circuit_test", [True]),
    ("log_tab_changed", ["tab_navigation", "      Expressão      "]),
    ("log_interactive_simplification_start", ["(~A+B)"]),
    ("log_law_applied", ["Identidade (A * 1 = A)", True, 1]),
    ("log_law_applied", ["Nula (A * 0 = 0)", False, 2]),
    ("log_simplification_step_failed", ["Nula (A * 0 = 0)", 2, "Lei não aplicável", "(~A+B)"]),
    ("log_simplification_skip", [1]),
    ("log_simplification_undo", []),
    ("log_simplification_completed", [1, 12.5]),
    ("log_equivalence_check_with_expressions", ["P>Q", "!P|Q", True]),
    ("log_equivalence_check_with_expressions", ["A&B", "A|B", False]),
    ("log_error", ["validation_error", "Empty expression"]),
    ("log_expression_entered", ["", False]),
    ("log_feature_used", ["problem_solved", 0]),
    ("log_feature_used", ["problem_answer_analysis", 0]),
]


def momentos():
    return [INICIO + 7.5 * (i + 1) for i in range(len(CHAMADAS))]


FIM = INICIO + 7.5 * (len(CHAMADAS) + 2)


def como_dados(id_usuario="aluno-123", plataforma="Navegador de teste", sistema="Windows", envio=None):
    return {
        "id_usuario": id_usuario,
        "plataforma": plataforma,
        "sistema": sistema,
        "inicio": INICIO,
        "fim": FIM,
        "fuso_minutos": FUSO_MINUTOS,
        "versao_app": "1.0-beta",
        "envio": envio,
        "chamadas": [
            {"metodo": metodo, "argumentos": argumentos, "momento": momento}
            for (metodo, argumentos), momento in zip(CHAMADAS, momentos())
        ],
    }

import threading
import itertools
import sys

try:
    with open(r"C:\Users\Otávio\Desktop\Estudo e Trabalho\Códigos\Gerador de Circuito Lógico\entrada.txt", "r") as file:
        expressao = file.read().strip()
except FileNotFoundError:
    print("O arquivo com a expressão não foi encontrado.")
    sys.exit()
    

def gerar_tabela_verdade(expressao):
    variaveis = sorted(set(filter(str.isalpha, expressao)))  # Extrai variáveis únicas
    
    def avaliar(expressao, valores):
        expressao_modificada = expressao
        for var, val in zip(variaveis, valores):
            expressao_modificada = expressao_modificada.replace(var, str(int(val)))
        expressao_modificada = (
            expressao_modificada.replace("&", " and ")
            .replace("|", " or ")
            .replace("!", " not ")
            .replace(">", " <= ")
        )
        return eval(expressao_modificada)
    
    combinacoes = list(itertools.product([False, True], repeat=len(variaveis)))
    resultados = [avaliar(expressao, valores) for valores in combinacoes]
    
    print("\nTabela Verdade:")
    print(" ".join(variaveis) + " | Resultado")
    print("-" * (len(variaveis) * 3 + 12))
    for valores, resultado in zip(combinacoes, resultados):
        print(" ".join(str(int(v)) for v in valores) + " | " + str(int(resultado)))
    
    if all(resultados):
        print("\nA expressão é uma TAUTOLOGIA.")
    elif any(resultados):
        print("\nA expressão é SATISFATÍVEL.")
    else:
        print("\nA expressão é uma CONTRADIÇÃO.")
    
def ver_circuito_pygame(expressao):
    def rodar_pygame():
        try:
            import circuito_logico
            if hasattr(circuito_logico, "plotar_circuito_logico"):
                circuito_logico.plotar_circuito_logico(expressao)
            else:
                print("Erro: A função 'plotar_circuito_logico' não foi encontrada no módulo 'circuito_logico'.")
        except ImportError as e:
            print(f"Erro ao importar 'circuito_logico': {e}")
    
    # Executa o Pygame em uma nova thread, pra o principal ainda ser o front
    threading.Thread(target=rodar_pygame).start()
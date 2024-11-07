import pygame
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox

# Função para iniciar o pygame e executar o circuito
def iniciar_circuito():
    # Oculta a janela principal do Tkinter enquanto o Pygame está em execução
    root.withdraw()

    # Caixa de diálogo para capturar a expressão proposicional
    expressao = simpledialog.askstring("Entrada", "Digite uma expressão proposicional (ex: P&Q|R):")
    if not expressao:
        messagebox.showinfo("Aviso", "Nenhuma expressão foi digitada.")
        root.deiconify()
        return
    
    pygame.init()

    # Configurações da tela
    screen_width, screen_height = 800, 400
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Circuito Lógico")

    # Cores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Funções de desenho das portas lógicas e demais funções (as mesmas definidas anteriormente)
    # Funções de desenho, conversão e lógica do circuito (usar as mesmas do código original)

    # Função de conversão para álgebra booleana
    def converter_para_algebra_booleana(expressao):
        # Lógica de conversão da expressão
        resultado = ""
        # Adicionar a lógica completa aqui (do código original)
        print("Expressão em Álgebra Booleana:", resultado)
        return resultado

    # Função para desenhar o circuito com base na expressão booleana
    def plotar_circuito_logico(expressao_booleana):
        # Lógica para desenhar o circuito no Pygame
        pass  # Adicione o código do circuito aqui

    # Convertendo a expressão para álgebra booleana
    expressao_booleana = converter_para_algebra_booleana(expressao)

    # Loop principal do Pygame
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)  # Limpa a tela
        plotar_circuito_logico(expressao_booleana)  # Desenha o circuito com base na expressão
        pygame.display.flip()  # Atualiza a tela

    pygame.quit()
    sys.exit()


# Configuração inicial do Tkinter
root = tk.Tk()
root.title("Circuito Lógico")
root.geometry("300x200")

# Criação do botão "Iniciar"
botao_iniciar = tk.Button(root, text="Iniciar Circuito", command=iniciar_circuito, font=("Arial", 14))
botao_iniciar.pack(pady=60)

# Inicia a interface do Tkinter
root.mainloop()


''' Aqui está uma explicação sobre o que foi feito para adicionar o botão "Iniciar Circuito" na interface Tkinter:

Configuração Inicial do Tkinter:

A janela principal do Tkinter (root) é criada e configurada com o título "Circuito Lógico".
A janela é dimensionada para 300x200 pixels com root.geometry("300x200"), proporcionando espaço suficiente para o botão.
Criação do Botão "Iniciar Circuito":

Um botão foi criado usando tk.Button, que cria um widget de botão em Tkinter.
O botão recebe o texto "Iniciar Circuito" e usa a fonte Arial com tamanho 14, especificada pelo argumento font=("Arial", 14).
O comando command=iniciar_circuito vincula o botão à função iniciar_circuito, de forma que, quando o botão é clicado, a função é executada.
Para centralizar o botão verticalmente na janela, botao_iniciar.pack(pady=60) é usado. O argumento pady=60 adiciona uma margem de 60 pixels em cima e embaixo do botão.
Início da Interface Gráfica:

A linha root.mainloop() é responsável por iniciar o loop principal da interface Tkinter, mantendo a janela aberta e respondendo a interações do usuário, como o clique no botão.
Comportamento da Função iniciar_circuito
Quando o botão "Iniciar Circuito" é clicado:

A função iniciar_circuito() é chamada. Ela oculta temporariamente a janela principal de Tkinter, usa simpledialog para capturar a expressão proposicional do usuário e abre o Pygame para exibir o circuito lógico.
'''

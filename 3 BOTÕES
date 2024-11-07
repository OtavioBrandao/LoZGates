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

    # Funções de desenho, conversão e lógica do circuito (usar as mesmas do código original)
    def converter_para_algebra_booleana(expressao):
        # Lógica de conversão da expressão
        resultado = ""
        print("Expressão em Álgebra Booleana:", resultado)
        return resultado

    def plotar_circuito_logico(expressao_booleana):
        pass  # Adicione o código do circuito aqui

    # Converte a expressão para álgebra booleana
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
    root.deiconify()  # Reabre a janela principal após o Pygame fechar
    exibir_botoes_adicionais()  # Exibe os novos botões após o fechamento do Pygame

# Função para exibir os botões adicionais
def exibir_botoes_adicionais():
    # Criação do botão para a transformação lógica
    botao_transformacao = tk.Button(root, text="Transformação Lógica", font=("Arial", 12), command=executar_transformacao)
    botao_transformacao.pack(pady=10)

    # Criação do botão para o caso de teste
    botao_caso_teste = tk.Button(root, text="Executar Caso de Teste", font=("Arial", 12), command=executar_caso_teste)
    botao_caso_teste.pack(pady=10)

# Função de exemplo para a transformação lógica
def executar_transformacao():
    # Aqui será implementada a lógica de transformação
    messagebox.showinfo("Transformação", "Executando transformação lógica...")

# Função de exemplo para o caso de teste
def executar_caso_teste():
    # Aqui será implementada a lógica do caso de teste
    messagebox.showinfo("Caso de Teste", "Executando caso de teste...")

# Configuração inicial do Tkinter
root = tk.Tk()
root.title("Circuito Lógico")
root.geometry("300x200")

# Criação do botão "Iniciar"
botao_iniciar = tk.Button(root, text="Iniciar Circuito", command=iniciar_circuito, font=("Arial", 14))
botao_iniciar.pack(pady=20)

# Inicia a interface do Tkinter
root.mainloop()



'''O código foi modificado para incluir dois novos botões na interface do Tkinter, que só aparecem depois que o usuário clica no botão "Iniciar Circuito" e fecha a tela do Pygame. Vamos detalhar cada parte do que foi feito:

Função iniciar_circuito():

Essa função é chamada ao clicar no botão "Iniciar Circuito" na janela principal.
A janela principal do Tkinter é temporariamente ocultada (root.withdraw()), enquanto o Pygame é iniciado e exibe a interface do circuito.
Após a captura da expressão proposicional, a expressão é convertida para álgebra booleana e o circuito correspondente é exibido no Pygame.
Quando o usuário fecha a janela do Pygame, a função exibir_botoes_adicionais() é chamada para reexibir a janela principal do Tkinter e adicionar os novos botões.
Função exibir_botoes_adicionais():

Após o Pygame encerrar, essa função é chamada para criar e exibir os dois novos botões na janela principal do Tkinter.
Os botões criados são:
Transformação Lógica (botao_transformacao): botão que aciona a função executar_transformacao, onde será implementada a lógica de transformação.
Executar Caso de Teste (botao_caso_teste): botão que aciona a função executar_caso_teste, onde será implementada a lógica do caso de teste.
Ambos os botões são configurados com estilo e espaçamento (pady=10) e são adicionados à janela.
Funções executar_transformacao e executar_caso_teste():

São funções de exemplo chamadas ao clicar nos botões adicionais. Por enquanto, exibem uma mensagem informando que estão em execução.
Você pode adicionar a lógica específica de transformação lógica ou o código do caso de teste dentro de cada função.
Reaparecimento da Janela Principal do Tkinter:

Ao final do iniciar_circuito(), a função root.deiconify() é chamada para reexibir a janela principal do Tkinter, seguida pela chamada para exibir_botoes_adicionais() para que os novos botões sejam exibidos.
Essa abordagem permite que a interface do Tkinter se expanda conforme necessário: o botão inicializa o Pygame e, ao final, exibe novos botões com funções adicionais que o usuário pode acionar para outras operações relacionadas ao circuito.
'''

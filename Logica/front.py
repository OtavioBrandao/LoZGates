import customtkinter as ctk
from PIL import Image  # Apenas Image, sem ImageTk
import threading

# Configuração inicial
ctk.set_appearance_mode("dark")  # Modo escuro
ctk.set_default_color_theme("blue")  # Tema azul

janela = ctk.CTk()
janela.title("Gerador de Portas Lógicas")
janela.geometry("1000x500")
janela.iconbitmap(r"C:\Users\laris\Desktop\Logica\icone.ico")
# Carregar a imagem com CTkImage
bg_image = ctk.CTkImage(Image.open(r"C:\Users\laris\Desktop\Logica\fundo.png"), size=(1000, 500))

# Função para alternar entre os frames
def show_frame(frame):
    frame.tkraise()
    
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

def clicked():
    expressao = entrada.get()
    if not expressao.strip():
        print("A expressão não pode estar vazia.")
        return
    with open(r"C:\Users\laris\Desktop\Logica\entrada.txt", "w") as file:
        file.write(expressao)
        
    #por algum motivo quando importa, vai direto pro outro codigo
    from converter import converter_para_algebra_booleana
    saida = converter_para_algebra_booleana(expressao)
    
    label = ctk.CTkLabel(
        janela, 
        text=f"Expressão em Álgebra Booleana:\n {saida}", 
        fg_color="#0534AA", 
        text_color="white", 
        font=("Arial", 16))
    label.place(x=360, y=240)
    
    ver_circuito = ctk.CTkButton(
        principal, 
        text="Ver Circuito Lógico", 
        fg_color="#1E90FF", 
        text_color="white", 
        hover_color="#8B008B", 
        width=200, 
        height=50, 
        font=("Arial", 16), 
        command=lambda: ver_circuito_pygame(saida))
    ver_circuito.place(x=100, y=300)

# Frames principais
frame_inicio = ctk.CTkFrame(
    janela, 
    width=1000, 
    height=500, 
    fg_color="#0534AA")

principal = ctk.CTkFrame(
    janela, 
    width=1000, 
    height=500, 
    fg_color="#0534AA")

frame_info = ctk.CTkFrame(
    janela, 
    width=1000, 
    height=500, 
    fg_color="#0534AA")


for frame in (frame_inicio, principal, frame_info):
    frame.place(x=0, y=0)
    
    bg_label = ctk.CTkLabel(
        frame, 
        image=bg_image, 
        text="")
    
    bg_label.place(
        x=0, 
        y=0, 
        relwidth=1, 
        relheight=1)

# ---------------- Frame de Início ----------------
# Frame interno para centralizar elementos

frame_inicio_conteudo = ctk.CTkFrame(
    frame_inicio, 
    fg_color="#0534AA", 
    corner_radius=30)

frame_inicio_conteudo.place(
    relx=0.5, 
    rely=0.5, 
    anchor="center")

label_inicio = ctk.CTkLabel(
    frame_inicio_conteudo, 
    text="Gerador\n de\n Portas Lógicas", 
    font=("Arial Bold", 30), 
    text_color="white", 
    fg_color="#0534AA")
label_inicio.pack(pady=20)

botao_start = ctk.CTkButton(
    frame_inicio_conteudo, 
    text="Start", 
    fg_color="#1E90FF", 
    text_color="white", 
    hover_color="#8B008B", 
    width=200, 
    height=50, 
    font=("Arial", 16), 
    command=lambda: show_frame(principal))
botao_start.pack(pady=10)

botao_info = ctk.CTkButton(
    frame_inicio_conteudo, 
    text="Info", 
    fg_color="#FFD700", 
    text_color="white", 
    hover_color="#8B008B", 
    width=200, 
    height=50, 
    font=("Arial", 16), 
    command=lambda: show_frame(frame_info))
botao_info.pack(pady=10)

# ---------------- Frame de Tarefas ----------------
label_tarefas = ctk.CTkLabel(
    principal, 
    text="Digite a expressão em Lógica Proposicional:", 
    font=("Arial Bold", 20), 
    text_color="white", 
    fg_color=None)
label_tarefas.place(x=300, y=130)

entrada = ctk.CTkEntry(
    principal, 
    width=300, 
    placeholder_text="Digite aqui", 
    font=("Arial", 14))
entrada.place(x=350, y=200)

bot = ctk.CTkButton(
    principal, 
    text="Confirmar", 
    fg_color="#1E90FF", 
    text_color="white", 
    hover_color="#8B008B", 
    width=200, 
    height=50, 
    font=("Arial", 16), 
    command=clicked)
bot.place(x=400, y=300)

botao_voltar1 = ctk.CTkButton(
    principal, 
    text="Voltar", 
    fg_color="goldenrod", 
    text_color="white", 
    hover_color="#8B008B", 
    width=200, 
    height=50, 
    font=("Arial", 16), 
    command=lambda: show_frame(frame_inicio))
botao_voltar1.place(x=400, y=400)

# ---------------- Frame de Informações ----------------
label_info = ctk.CTkLabel(
    frame_info, 
    text="Integrantes do Grupo:\nOtávio, Larissa, Zilderlan e Narel.", 
    font=("Arial", 20), 
    text_color="white", 
    fg_color=None)
label_info.place(x=355, y=120)

label_info2 = ctk.CTkLabel(
    frame_info, 
    text="Átomos aceitos:\nP, Q, R, S e T.\n\nRepresentação de simbolos:\n'&' (e), '|' (ou), '!' (não) e '>' (implica).\n\nAtenção:\nParênteses funciona.", 
    font=("Arial", 20), 
    text_color="white", 
    fg_color=None)
label_info2.place(x=355, y=200)

botao_voltar2 = ctk.CTkButton(
    frame_info, 
    text="Voltar", 
    fg_color="#FFD700", 
    text_color="white", 
    hover_color="#8B008B", 
    width=200, 
    height=50, 
    font=("Arial", 16), 
    command=lambda: show_frame(frame_inicio))
botao_voltar2.place(x=400, y=400)

# Exibe o frame inicial
show_frame(frame_inicio)

# Loop principal
janela.mainloop()
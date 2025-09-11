import customtkinter as ctk


class Button:
    def __init__(self, nome, comando, botao):
        self.nome = nome
        self.comando = comando
        self.botao = botao
    
    @staticmethod
    def botao_duvida(frame):
        botao = ctk.CTkButton(
            frame,
            text="❓",
            fg_color="#ADD8E6",
            text_color="#000080",
            hover_color="#8B008B",
            border_width=2,
            border_color="#708090",
            width=50,
            height=50,
            font=("Trebuchet MS", 16),
            corner_radius=25,  
        )
        return botao

    @staticmethod
    def botao_voltar(nome, frame):
        botao = ctk.CTkButton(
            frame,
            text=nome,
            fg_color="goldenrod",
            text_color="#000080",
            hover_color="#8B008B",
            border_width=2,
            border_color="#708090",
            width=200,
            height=50,
            font=("Trebuchet MS", 16),
        )
        return botao
    
    @staticmethod
    def botao_padrao(nome, frame):
        botao = ctk.CTkButton(
            frame,
            text=nome,
            fg_color="#B0E0E6",
            text_color="#000080",
            hover_color="#8B008B",
            border_width=2,
            border_color="#708090",
            width=200,
            height=50,
            font=("Trebuchet MS", 16),
        )
        return botao
    
    @staticmethod
    def botao_facil(nome, frame):
        pass
    def botao_dificil(nome, frame):
        pass
    def botao_medio(nome, frame):
        pass

    
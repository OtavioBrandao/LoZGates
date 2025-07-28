import customtkinter as CTK


class Button:
    def __init__(self, nome, comando, botao):
        self.nome = nome
        self.comando = comando
        self.botao = botao

    def botao_voltar(self, nome, comando, botao, frame):
        botao = CTK.CTkButton(
            frame,
            text=nome,
            command=lambda: comando,
            fg_color="goldenrod",
            text_color="#000080",
            hover_color="#8B008B",
            border_width=2,
            border_color="#708090",
            width=200,
            height=50,
            font=("Arial", 16),
        )
        return botao

    def botao_padrao(self, nome, comando, botao, frame):
        botao = CTK.CTkButton(
            frame,
            text=nome,
            command=comando,
            fg_color="#B0E0E6",
            text_color="#000080",
            hover_color="#8B008B",
            border_width=2,
            border_color="#708090",
            width=200,
            height=50,
            font=("Arial", 16),
        )
        return botao
       
    
    def posicionar_botao_place(self, botao, x, y):
        botao.place(x=x, y=y)
        return botao
    def posicionar_botao_grid(self, botao, row, column):
        botao.grid(row=row, column=column, padx=10, pady=10)
        return botao
    def posicionar_botao_pack(self, botao):
        botao.pack(pady=10)
        return botao
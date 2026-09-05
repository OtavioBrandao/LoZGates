with open('FrontEnd/interface.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if 'frame_inicio = ctk.CTkFrame' in line:
        new_lines.append('    from FrontEnd.screens.home.home_screen import HomeScreen\n')
        new_lines.append('    frame_inicio = HomeScreen(janela, navigation, janela)\n')
        continue
    if 'frame_inicio.grid(row=0' in line:
        continue
    if '#---------------- FRAME DE INÍCIO ----------------' in line:
        skip = True
        continue
    if skip and 'botao_info.pack(fill=' in line and 'Spacing.XXL' in line:
        skip = False
        continue
    if not skip:
        new_lines.append(line)

with open('FrontEnd/interface.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

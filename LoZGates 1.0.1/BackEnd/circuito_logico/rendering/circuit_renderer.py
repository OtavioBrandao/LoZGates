"""
    Módulo para renderização automática de circuitos lógicos baseado na AST.
    Gera visualizações estáticas dos circuitos com layout automático.
"""

from ..logic.parser import criar_ast_de_expressao, calcular_layout_dinamico, _coletar_variaveis

def desenhar_circuito_dinamico(layout, x_pos, bus_positions, drawer):
    layout_type = layout.get('type')
    
    if layout_type in ['variable', 'negated_variable']:
        bus_name = layout['name'] if layout_type == 'variable' else f"~{layout['name']}"
        return {
            'type': 'bus_connection', 
            'bus_x': bus_positions.get(bus_name, 50), 
            'y_pos': layout['y_pos'] + 40
        }
    
    if layout_type == 'gate':
        gate_center_y = layout['y_pos']
        gate_top_y = gate_center_y - drawer.GATE_HEIGHT / 2
        
        # Mapeia operadores para nomes de portas
        op_map = {'*': 'AND', '+': 'OR', '~': 'NOT'}
        output_pos = drawer.draw_gate_shape(op_map[layout['op']], x_pos, gate_top_y)
        
        num_inputs = len(layout['children'])
        
        # Calcula posições de entrada
        if num_inputs == 1:
            input_positions = [(x_pos, gate_center_y)]
        else:
            spacing = (drawer.GATE_HEIGHT - 30) / (num_inputs - 1) if num_inputs > 1 else 0
            input_positions = [
                (x_pos, (gate_top_y + 15) + spacing * i) 
                for i in range(num_inputs)
            ]
        
        # Desenha conexões dos filhos
        for i, child_layout in enumerate(layout['children']):
            child_output = desenhar_circuito_dinamico(
                child_layout, 
                x_pos - drawer.NODE_H_SPACING, 
                bus_positions, 
                drawer
            )
            
            if child_output['type'] == 'bus_connection':
                bus_pos = (child_output['bus_x'], child_output['y_pos'])
                drawer.draw_smart_wire(bus_pos, input_positions[i])
                drawer.draw_connection_dot(bus_pos)
            else:
                drawer.draw_smart_wire(
                    (child_output['x'], child_output['y']), 
                    input_positions[i]
                )
        
        return {'type': 'gate_output', 'x': output_pos[0], 'y': output_pos[1]}
    
    return {}


def desenhar_circuito_logico_base(expressao_booleana, drawer, screen_width, screen_height):
    try:
        ast_root = criar_ast_de_expressao(expressao_booleana)
    except ValueError as e:
        drawer.draw_text(f"Erro: {e}", (screen_width/2, screen_height/2), 40, (255, 80, 80))
        return
    
    # Coleta variáveis e cria barramentos
    variaveis = sorted(list(_coletar_variaveis(ast_root)))
    bus_positions = {}
    bus_x_start = 100
    bus_spacing = 100
    last_bus_x = bus_x_start
    
    # Desenha os barramentos de variáveis
    for i, var_name in enumerate(variaveis):
        # Barramento da variável normal
        true_bus_x = bus_x_start + i * bus_spacing
        drawer.draw_line((true_bus_x, 40), (true_bus_x, screen_height * 3), drawer.WHITE, 2)
        drawer.draw_text(var_name, (true_bus_x, 25))
        bus_positions[var_name] = true_bus_x
        
        # Barramento da variável negada
        negated_bus_x = true_bus_x + 40
        drawer.draw_line((negated_bus_x, 40), (negated_bus_x, screen_height * 3), drawer.WHITE, 2)
        drawer.draw_text(f"~{var_name}", (negated_bus_x, 25))
        bus_positions[f"~{var_name}"] = negated_bus_x
        last_bus_x = negated_bus_x
    
    # Calcula layout e desenha circuito
    layout = calcular_layout_dinamico(ast_root, y_base=100)
    primeiro_gate_x = last_bus_x + 150
    final_output = desenhar_circuito_dinamico(
        layout, 
        primeiro_gate_x + layout.get('width', 0), 
        bus_positions, 
        drawer
    )
    
    # Desenha a saída final
    if final_output and final_output.get('type') == 'gate_output':
        pos = (final_output['x'], final_output['y'])
        drawer.draw_line(pos, (pos[0] + 80, pos[1]), drawer.WHITE, 4)
        drawer.draw_text("SAÍDA", (pos[0] + 120, pos[1]), 30, drawer.WHITE)


def draw_ui_info(screen, camera, font):
    ui_texts = [
        "Controles:",
        "- Arrastar: Mouse esquerdo",
        "- Zoom: Roda do mouse", 
        "- WASD: Mover câmera",
        "- R: Resetar vista",
        f"Zoom: {camera.zoom:.2f}x"
    ]
    
    y = 10
    for text in ui_texts:
        try:
            surface = font.render(text, True, (255, 255, 255))
            screen.blit(surface, (10, y))
            y += 25
        except: 
            pass
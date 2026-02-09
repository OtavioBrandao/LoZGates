"""
Arquivo principal do módulo de circuitos lógicos.
Contém as funções de compatibilidade para integração com a interface gráfica.
"""
import pygame
import os
from PIL import Image, ImageOps

from BackEnd.circuito_logico.rendering.camera import Camera
from BackEnd.circuito_logico.rendering.drawer import CircuitDrawer
from BackEnd.circuito_logico.rendering.circuit_renderer import desenhar_circuito_logico_base
from BackEnd.circuito_logico.interactive.interactive_circuit import CircuitoInterativoManual
from BackEnd.circuito_logico.static.static_circuit import CircuitoInterativo
from .converter import converter_para_algebra_booleana


def plotar_circuito_logico(expressao, x_offset=0, width=1200, height=800):
    from config import ASSETS_PATH
    try:
        if not pygame.get_init():
            pygame.init()
            pygame.font.init()
        
        #Cria uma superfície temporária para calcular as dimensões do circuito
        temp_screen = pygame.Surface((width, height))
        temp_camera = Camera(width, height)
        temp_drawer = CircuitDrawer(temp_screen, temp_camera)
        
        expressao_booleana = converter_para_algebra_booleana(expressao)
        
        #Calcula o layout e as dimensões do circuito
        try:
            from BackEnd.circuito_logico.logic.parser import criar_ast_de_expressao, calcular_layout_dinamico, _coletar_variaveis
            
            ast_root = criar_ast_de_expressao(expressao_booleana)
            variaveis = sorted(list(_coletar_variaveis(ast_root)))
            
            #Calcula posições dos barramentos
            bus_x_start = 100
            bus_spacing = 100
            last_bus_x = bus_x_start + (len(variaveis) - 1) * bus_spacing + 40
            
            layout = calcular_layout_dinamico(ast_root, y_base=100)
            primeiro_gate_x = last_bus_x + 150
            circuit_end_x = primeiro_gate_x + layout.get('width', 0) + 200  #+200 para saída
            
            #Calcula o centro do circuito
            circuit_center_x = (bus_x_start + circuit_end_x) / 2
            circuit_center_y = layout['y_pos']
            
            #Ajusta a câmera para centralizar o circuito
            temp_camera.x = circuit_center_x
            temp_camera.y = circuit_center_y
            
            #Calcula o zoom necessário para mostrar todo o circuito
            circuit_width = circuit_end_x - bus_x_start
            circuit_height = layout['height'] + 200  #margem extra
            
            zoom_x = width / circuit_width
            zoom_y = height / circuit_height
            optimal_zoom = min(zoom_x, zoom_y, 1.5) * 0.8  #0.8 para margem
            
            temp_camera.zoom = max(0.2, min(3.0, optimal_zoom))
            
        except Exception as e:
            print(f"Erro ao calcular layout: {e}")
            #Usa valores padrão se houver erro
            temp_camera.x = 400
            temp_camera.y = 300
            temp_camera.zoom = 1.0
        
        #Cria a superfície final com a câmera ajustada
        screen = pygame.Surface((width, height))
        screen.fill((0, 0, 0))
        drawer = CircuitDrawer(screen, temp_camera)
        
        desenhar_circuito_logico_base(expressao_booleana, drawer, width, height)
        
        caminho_img = os.path.join(ASSETS_PATH, "circuito.png")
        pygame.image.save(screen, caminho_img)
        
    except Exception as e:
        print(f"Erro ao plotar circuito estático: {e}")
        raise


def criar_circuito_integrado(parent_frame, expressao):
    expressao_booleana = converter_para_algebra_booleana(expressao)
    return CircuitoInterativoManual(parent_frame, expressao_booleana)


def criar_circuito_estatico(parent_frame, expressao):
    expressao_booleana = converter_para_algebra_booleana(expressao)
    return CircuitoInterativo(parent_frame, expressao_booleana)


#Manter compatibilidade com nomes antigos
def ver_circuito_pygame(expressao):
    return plotar_circuito_logico(expressao)
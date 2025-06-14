import pygame
import sys

# Inicializa o pygame
pygame.init()

x_offset = 80
y_offset = 20

BLACK = (0, 0, 0)

# Configurações da tela
screen_width, screen_height = 800, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Circuito Lógico")

def draw_and_gate(x, y):
    pygame.draw.line(screen, BLACK, (x, y), (x, y + 80), 5)
    pygame.draw.line(screen, BLACK, (x, y), (x + 40, y), 5)
    pygame.draw.line(screen, BLACK, (x, y + 80), (x + 40, y + 80), 5)
    pygame.draw.arc(screen, BLACK, (x + 20, y, 40, 80), -1.57, 1.57, 5)
    pygame.draw.line(screen, BLACK, (x + 60, y + 40), (x + 80, y + 40), 5)

def draw_or_gate(x, y):
    pygame.draw.line(screen, BLACK, (x, y), (x + 40, y), 5)
    pygame.draw.line(screen, BLACK, (x, y + 80), (x + 40, y + 80), 5)
    pygame.draw.arc(screen, BLACK, (x + 20, y, 40, 80), -1.57, 1.57, 5)
    pygame.draw.arc(screen, BLACK, (x - 20, y, 40, 80), -1.57, 1.57, 5)
    pygame.draw.line(screen, BLACK, (x + 60, y + 40), (x + 80, y + 40), 5)

def draw_not_gate(x, y):
    pygame.draw.polygon(screen, BLACK, [(x, y), (x, y + 80), (x + 50, y + 40)], 5)
    pygame.draw.circle(screen, BLACK, (x + 60, y + 40), 10, 5)

def draw_nand_gate(x, y):
    draw_and_gate(x, y)
    pygame.draw.circle(screen, BLACK, (x + 80, y + 40), 10, 5)

def draw_nor_gate(x, y):
    draw_or_gate(x, y)
    pygame.draw.circle(screen, BLACK, (x + 75, y + 40), 10, 5)

def draw_xor_gate(x, y):
    draw_or_gate(x, y)
    pygame.draw.arc(screen, BLACK, (x - 35, y, 40, 80), -1.57, 1.57, 5)

def draw_xnor_gate(x, y):
    draw_xor_gate(x, y)
    pygame.draw.circle(screen, BLACK, (x + 80, y + 40), 10, 5)

def draw_label(x, y, text):
    font = pygame.font.Font(None, 36)  
    text = font.render(text, True, BLACK)  
    text_rect = text.get_rect(center=(x, y))  
    screen.blit(text, text_rect.topleft)

draws = {
    '&': draw_and_gate,
    '|': draw_or_gate,
    '~': draw_not_gate,
    'L': draw_label}

class output:
    def __init__(self, left_exp, right_exp, operator, x, y):
        self.left_exp = left_exp
        self.right_exp = right_exp
        self.operator = operator
        self.x = x
        self.y = y
    def draw(self):
        
        if self.operator == "L":
            font = pygame.font.Font(None, 36)  
            text = font.render(self.right_exp, True, BLACK)  
            text_rect = text.get_rect(center=(self.x + 70, self.y + 40))  
            screen.blit(text, text_rect.topleft)
            return 
        
        if self.operator == "~":
            draw_not_gate(self.x, self.y)
            if(not self.right_exp.isnumeric()):
                font = pygame.font.Font(None, 36)
                text = font.render(self.right_exp, True, BLACK)
                text_rect = text.get_rect(center=(self.x - 20, self.y + 40))
                screen.blit(text, text_rect.topleft)
            else:
                self.x = output_list[int(self.right_exp)].x + 100
                self.y = output_list[int(self.right_exp)].y + 100
                distance = self.x - output_list[int(self.right_exp)].x + 80
                
                pygame.draw.line(screen, BLACK, (self.x, self.y + 40) , ((output_list[int(self.right_exp)].x + distance / 2) , self.y + 40), 5)
                pygame.draw.line(screen, BLACK, ((output_list[int(self.right_exp)].x + distance / 2), output_list[int(self.right_exp)].y + 40) , (output_list[int(self.right_exp)].x + 80, output_list[int(self.right_exp)].y + 40), 5)
                pygame.draw.line(screen, BLACK, ((output_list[int(self.right_exp)].x + distance / 2), output_list[int(self.right_exp)].y + 40) ,((output_list[int(self.right_exp)].x + distance / 2) , self.y + 40), 5)

            return
        
        if(not self.left_exp.isnumeric()):
            pygame.draw.line(screen, BLACK, (self.x, self.y + 20) , (self.x - 20, self.y + 20), 5)
            font = pygame.font.Font(None, 36)  
            text = font.render(self.left_exp, True, BLACK)  
            text_rect = text.get_rect(center=(self.x - 30, self.y + 20))  
            screen.blit(text, text_rect.topleft)
        else:
            self.x = output_list[int(self.left_exp)].x + 200
            self.y = output_list[int(self.left_exp)].y + 100
            
            distance = self.x - output_list[int(self.left_exp)].x + 80
            
            pygame.draw.line(screen, BLACK, (self.x, self.y + 20) , ((output_list[int(self.left_exp)].x + distance / 2) , self.y + 20), 5)
            pygame.draw.line(screen, BLACK, ((output_list[int(self.left_exp)].x + distance / 2), self.y + 20) , ((output_list[int(self.left_exp)].x + distance / 2), output_list[int(self.left_exp)].y + 40), 5)
            pygame.draw.line(screen, BLACK, ((output_list[int(self.left_exp)].x + distance / 2), output_list[int(self.left_exp)].y + 40) , (output_list[int(self.left_exp)].x + 80, output_list[int(self.left_exp)].y + 40), 5)
        
        if(not self.right_exp.isnumeric()):
            pygame.draw.line(screen, BLACK, (self.x, self.y + 60) , (self.x - 20, self.y + 60), 5)
            font = pygame.font.Font(None, 36)  
            text = font.render(self.right_exp, True, BLACK)  
            text_rect = text.get_rect(center=(self.x - 30, self.y + 60))  
            screen.blit(text, text_rect.topleft)
        else:
            distance = self.x - output_list[int(self.right_exp)].x + 80
            
            pygame.draw.line(screen, BLACK, (self.x, self.y + 60) , ((output_list[int(self.right_exp)].x + distance / 2) , self.y + 60), 5)
            pygame.draw.line(screen, BLACK, ((output_list[int(self.right_exp)].x + distance / 2), self.y + 60) , ((output_list[int(self.right_exp)].x + distance / 2), output_list[int(self.right_exp)].y + 40), 5)
            pygame.draw.line(screen, BLACK, ((output_list[int(self.right_exp)].x + distance / 2), output_list[int(self.right_exp)].y + 40) , (output_list[int(self.right_exp)].x + 80, output_list[int(self.right_exp)].y + 40), 5)
            
        draws[self.operator](self.x, self.y)
        
        

output_list = []

def process_input(input_str):
    # Pilha para controlar o nível de aninhamento dos parênteses
    stack = []
    
    expressions = []
    
    
    for i, char in enumerate(input_str):
        if char == '(':
            stack.append(i)
        elif char == ')':
            if not stack:
                print("Expressão inválida: Aninhamento inválido")
                return
            print(f"Aninhamento entre {stack[-1]} e {i}")
            
            for j, expression in enumerate(expressions):
                if expression in input_str[stack[-1]+1:i]:
                    print("Expressão encontrada:", expression)
                    print("input_str[stack[-1]+1:i]:", input_str[stack[-1]+1:i])
                    
                    size = len(expression)
                    
                    input_str = input_str.replace(expression, f"{str(j)}{' ' * (size - len(str(j)))}")
                    
                    print("input_str:", input_str)
            
            expressions.append(input_str[stack[-1]+1:i])
            print("opa", input_str[stack[-1]+1:i])
            
            stack.pop()
    
    if stack:
        print("Expressão inválida: Aninhamento inválido")
    else:
        print(expressions)
        print("Expressão válida")
        
    return expressions
    

def process_expressions(expressions):

    global x_offset
    global y_offset

    for i in expressions:
        i = i.replace(" ", "")
        i = i.replace("(", "")
        i = i.replace(")", "")
        right_exp = ""
        left_exp = ""
        operator = ""
        
        if len(i) == 1:
            output_list.append(output("", i, "L", x_offset, y_offset))
        
        if "&" in i:
            operator = "&"
            index = i.index("&")
            right_exp = i[index+1:]
            left_exp = i[:index]
         
            output_list.append(output(left_exp, right_exp, operator, x_offset, y_offset))
            y_offset += 100
                
        if "|" in i:
            operator = "|"
            index = i.index("|")
            right_exp = i[index+1:]
            left_exp = i[:index]
                
            output_list.append(output(left_exp, right_exp, operator, x_offset, y_offset))
            y_offset += 100
                
            print(f"{left_exp}{operator}{right_exp}")
        
        if "~" in i:
            operator = "~"
            index = i.index("~")
            right_exp = i[index+1:]
            left_exp = i[:index]
            
            print(f"{left_exp}{operator}{right_exp}")
            output_list.append(output(left_exp, right_exp, operator, x_offset, y_offset))
            y_offset += 100
    
    
            

# Teste da função com a entrada fornecida
print("Forneça um entrada do tipo: ((C|D)&(~(A&B)))")
input_str = str(input()) #input_str = "((C|D)&(~(A&B)))"
exp = process_input(input_str)
process_expressions(exp)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((255, 255, 255))  # Limpa a tela
    
    for output in output_list:
        print(output.left_exp, output.right_exp, output.operator, output.x, output.y)
        output.draw()

    pygame.display.flip()  # Atualiza a tela

pygame.quit()
sys.exit()

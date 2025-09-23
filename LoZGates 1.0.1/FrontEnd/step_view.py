# StepView - Componente para visualização passo a passo da simplificação
# Substitui o log de terminal por uma interface visual limpa

import customtkinter as ctk
import re
from .design_tokens import Colors, Typography, Dimensions, Spacing, get_font, get_title_font

class StepView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=Colors.PRIMARY_BG)
        
        # Configurar grid para expansão
        self.grid_rowconfigure(0, weight=0)  # header
        self.grid_rowconfigure(1, weight=1)  # scroll deve expandir
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = ctk.CTkLabel(
            self,
            text="Progresso da Simplificação",
            font=get_title_font(Typography.SIZE_TITLE_SMALL),
            text_color=Colors.TEXT_PRIMARY
        )
        self.header.grid(row=0, column=0, pady=(Spacing.MD, Spacing.SM))
        
        # Área scrollável para os passos
        self.scroll_area = ctk.CTkScrollableFrame(
            self,
            fg_color=Colors.SURFACE_DARK,
            corner_radius=Dimensions.CORNER_RADIUS_MEDIUM
        )
        self.scroll_area.grid(row=1, column=0, sticky="nsew", padx=Spacing.MD, pady=(0, Spacing.SM))
        self.scroll_area.configure(height=500)
        
        # Rodapé (inicialmente oculto)
        self.footer = ctk.CTkFrame(self, fg_color=Colors.SURFACE_MEDIUM, corner_radius=Dimensions.CORNER_RADIUS_MEDIUM)
        
        self._steps = []
        self.current_iteration = 0
        
    def reset(self, original_expression: str) -> None:
        """Reinicia a visualização com uma nova expressão"""
        # Limpa passos anteriores
        for widget in self.scroll_area.winfo_children():
            widget.destroy()
        
        # Esconde rodapé
        self.footer.pack_forget()
        
        # Mostra expressão inicial
        initial_frame = ctk.CTkFrame(self.scroll_area, fg_color=Colors.SURFACE_LIGHT, corner_radius=Dimensions.CORNER_RADIUS_SMALL)
        initial_frame.pack(fill="x", padx=Spacing.SM, pady=Spacing.XS)
        
        title_label = ctk.CTkLabel(
            initial_frame,
            text="Expressão Inicial",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        title_label.pack(pady=(Spacing.SM, Spacing.XS))
        
        expr_label = ctk.CTkLabel(
            initial_frame,
            text=original_expression,
            font=get_font(Typography.SIZE_BODY),
            text_color=Colors.TEXT_PRIMARY
        )
        expr_label.pack(pady=(0, Spacing.SM))
        
        self._steps = []
        self.current_iteration = 0
        
    def append_step(self, step: dict) -> None:
        """Adiciona um novo passo à visualização"""
        # Numeração automática
        n = len(self._steps) + 1
        step = {**step, "iteration": n}
        self._steps.append(step)
        
        step_frame = ctk.CTkFrame(self.scroll_area, fg_color=Colors.SURFACE_LIGHT, corner_radius=Dimensions.CORNER_RADIUS_SMALL)
        step_frame.pack(fill="x", padx=Spacing.SM, pady=Spacing.XS)
        
        # Título com iteração e lei
        title_text = f"Iteração {n} — {step['law']}"
        title_label = ctk.CTkLabel(
            step_frame,
            text=title_text,
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        title_label.pack(pady=(Spacing.SM, Spacing.XS), padx=Spacing.SM, anchor="w")
        
        # Subexpressão alvo
        if step.get('subexpression'):
            sub_label = ctk.CTkLabel(
                step_frame,
                text=f"Subexpressão: {step['subexpression']}",
                font=get_font(Typography.SIZE_BODY_SMALL),
                text_color=Colors.TEXT_SECONDARY
            )
            sub_label.pack(pady=(0, Spacing.XS), padx=Spacing.SM, anchor="w")
        
        # Antes → Depois
        transform_frame = ctk.CTkFrame(step_frame, fg_color=Colors.SURFACE_DARK, corner_radius=Dimensions.CORNER_RADIUS_SMALL)
        transform_frame.pack(fill="x", padx=Spacing.SM, pady=Spacing.XS)
        
        transform_text = f"{step['before']} → {step['after']}"
        transform_label = ctk.CTkLabel(
            transform_frame,
            text=transform_text,
            font=get_font(Typography.SIZE_BODY_SMALL),
            text_color=Colors.TEXT_PRIMARY,
            wraplength=700
        )
        transform_label.pack(pady=Spacing.SM, padx=Spacing.SM)
        
        # Status e nota
        status_frame = ctk.CTkFrame(step_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=(Spacing.XS, Spacing.SM), padx=Spacing.SM)
        
        # Ícone de status
        status_icon = "✔" if step['success'] else "✖"
        status_color = Colors.SUCCESS if step['success'] else Colors.ERROR
        
        status_label = ctk.CTkLabel(
            status_frame,
            text=status_icon,
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=status_color
        )
        status_label.pack(side="left", padx=(0, Spacing.XS))
        
        # Nota (se existir)
        if step.get('note'):
            note_label = ctk.CTkLabel(
                status_frame,
                text=step['note'],
                font=get_font(Typography.SIZE_CAPTION),
                text_color=Colors.TEXT_SECONDARY
            )
            note_label.pack(side="left", padx=Spacing.XS)

        
    def finalize(self, final_expression: str, success: bool, stats: dict = None) -> None:
        """Finaliza a visualização com resultado e estatísticas"""
        # Rodapé com resultado
        self.footer.grid(row=2, column=0, sticky="ew", padx=Spacing.MD, pady=(Spacing.SM, Spacing.MD))
        self.grid_rowconfigure(2, weight=0)
        
        # Limpa rodapé anterior
        for widget in self.footer.winfo_children():
            widget.destroy()
        
        # Título do resultado
        result_title = ctk.CTkLabel(
            self.footer,
            text="Expressão Resultante",
            font=get_font(Typography.SIZE_BODY, Typography.WEIGHT_BOLD),
            text_color=Colors.TEXT_ACCENT
        )
        result_title.pack(pady=(Spacing.SM, Spacing.XS))
        
        # Expressão final
        final_label = ctk.CTkLabel(
            self.footer,
            text=final_expression,
            font=get_font(Typography.SIZE_BODY),
            text_color=Colors.TEXT_PRIMARY,
            wraplength=800
        )
        final_label.pack(pady=(0, Spacing.SM), padx=Spacing.SM)
        
        # Mensagem de status
        if not success or len(self._steps) == 0:
            status_msg = ctk.CTkLabel(
                self.footer,
                text="Nenhuma simplificação adicional foi identificada.",
                font=get_font(Typography.SIZE_BODY_SMALL),
                text_color=Colors.TEXT_SECONDARY
            )
            status_msg.pack(pady=(0, Spacing.SM))
        
        # Estatísticas simplificadas - apenas iterações
        if len(self._steps) > 0:
            iter_label = ctk.CTkLabel(
                self.footer,
                text=f"Iterações: {len(self._steps)}",
                font=get_font(Typography.SIZE_CAPTION),
                text_color=Colors.TEXT_SECONDARY
            )
            iter_label.pack(pady=(0, Spacing.SM))


class StepParser:
    """Parser para converter logs de texto em eventos de passo"""
    
    def __init__(self, step_view: StepView):
        self.step_view = step_view
        self.current_iteration = 0
        self.current_step = {}
        self.original_expr = ""
        self.previous_expr = ""
        self.laws_applied = 0
        self.final_expr = ""
        
    def parse_log_line(self, line: str) -> None:
        """Processa uma linha do log e extrai informações de passo"""
        line = line.strip()
        if not line:
            return
            
        # Detecta início de iteração
        iteration_match = re.search(r'Iteração (\d+):\s*tentando simplificar\s*(.+)', line)
        if iteration_match:
            self.current_iteration = int(iteration_match.group(1))
            self.previous_expr = iteration_match.group(2).strip()
            return
            
        # Detecta aplicação de lei (formato: "Aplicando Lei em 'antes' -> 'depois'")
        law_match = re.search(r'Aplicando\s+(.+?)\s+em\s+\'(.+?)\'\s*->\s*\'(.+?)\'', line)
        if law_match:
            law_name = law_match.group(1).strip()
            before_expr = law_match.group(2).strip()
            after_expr = law_match.group(3).strip()
            
            step = {
                'law': law_name,
                'subexpression': before_expr,
                'before': before_expr,
                'after': after_expr,
                'success': True,
                'note': None
            }
            self.step_view.append_step(step)
            self.laws_applied += 1
            return
            
        # Detecta árvore intermediária (resultado da iteração)
        tree_match = re.search(r'Árvore intermediária:\s*(.+)', line)
        if tree_match:
            result_expr = tree_match.group(1).strip()
            return
            
        # Detecta fim da simplificação
        if "Nenhuma outra simplificação foi possível" in line:
            return
            
        # Detecta expressão original
        if "Expressão Original:" in line:
            expr_match = re.search(r'Expressão Original\s*:\s*(.+)', line)
            if expr_match:
                self.original_expr = expr_match.group(1).strip()
            return
            
        # Detecta expressão simplificada final
        if "Expressão Simplificada:" in line:
            expr_match = re.search(r'Expressão Simplificada:\s*(.+)', line)
            if expr_match:
                self.final_expr = expr_match.group(1).strip()
            return
            
    def finalize_parsing(self, fallback_expression: str, success: bool = True) -> None:
        """Finaliza o parsing e chama finalize no step_view"""
        final_expression = self.final_expr if self.final_expr else fallback_expression
        
        # Se não houve leis aplicadas, indica que não houve simplificação
        actual_success = success and self.laws_applied > 0
        
        stats = {}
        self.step_view.finalize(final_expression, actual_success, stats)
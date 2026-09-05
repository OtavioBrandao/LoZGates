import customtkinter as ctk
from typing import Dict, Any

# Ajuste dos imports
from config import make_window_visible_robust
from FrontEnd.utils.responsive import calculate_window_layout

class DetailedDataSharingDialog:
    """
    Diálogo para solicitar a permissão do usuário para enviar dados de atividade.
    Mostra um preview estruturado dos dados que serão enviados.
    """
    def __init__(self, logger):
        self.logger = logger
        self.result = None
    
    def show_dialog(self) -> bool: #Mostra dialog com preview detalhado dos dados.
        root = ctk.CTkToplevel()
        make_window_visible_robust(root, modal=True)
        root.title("Compartilhamento de dados detalhados - LoZ Gates Beta")
        layout = calculate_window_layout(
            root.winfo_screenwidth(),
            root.winfo_screenheight(),
            preferred=(800, 700),
            minimum=(520, 480),
        )
        root.geometry(layout.geometry)
        root.minsize(layout.minimum_width, layout.minimum_height)
        root.resizable(True, True)
        
        main_frame = ctk.CTkScrollableFrame(root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            main_frame, 
            text="📊 Dados detalhados de uso - LoZ Gates Beta",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        explanation = ctk.CTkTextbox(main_frame, height=100, wrap="word")
        explanation.pack(fill="x", pady=(0, 20))
        
        explanation_text = """Seus dados de uso detalhados nos ajudam a entender melhor como melhorar o LoZ Gates. 
        Todos os dados são ANÔNIMOS e incluem estatísticas sobre uso de funcionalidades, padrões de interação e tipos de problemas resolvidos.
        Abaixo você pode ver exatamente o que será enviado:"""
        
        explanation.insert("1.0", explanation_text)
        explanation.configure(state="disabled")
        
        #Preview dos dados - SOMENTE SESSÃO ATUAL
        summary = self.logger.get_current_session_summary()
        if summary:
            data_frame = ctk.CTkFrame(main_frame)
            data_frame.pack(fill="x", pady=(0, 20))
            
            data_title = ctk.CTkLabel(
                data_frame,
                text="📈 Preview dos Dados que Serão Enviados:",
                font=ctk.CTkFont(weight="bold")
            )
            data_title.pack(pady=10)
            
            #Cria preview estruturado dos dados
            preview_text = self._create_data_preview(summary)
            
            preview_box = ctk.CTkTextbox(data_frame, height=300, wrap="word")
            preview_box.pack(fill="x", padx=10, pady=10)
            preview_box.insert("1.0", preview_text)
            preview_box.configure(state="disabled")
        
        #Botões
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=20)
        
        def on_send():
            self.result = True
            root.destroy()
        
        def on_cancel():
            self.result = False
            root.destroy()
        
        def on_never():
            self.result = "never"
            root.destroy()
        
        send_btn = ctk.CTkButton(
            button_frame,
            text="✅ Enviar Dados Detalhados (Ajudar)",
            command=on_send,
            fg_color="#4CAF50"
        )
        send_btn.pack(side="left", padx=5, pady=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Não Agora",
            command=on_cancel,
            fg_color="#FF9800"
        )
        cancel_btn.pack(side="left", padx=5, pady=10)
        
        never_btn = ctk.CTkButton(
            button_frame,
            text="🚫 Nunca Perguntar",
            command=on_never,
            fg_color="#F44336"
        )
        never_btn.pack(side="left", padx=5, pady=10)
        
        #Informações adicionais
        info_text = """💡 Seus dados detalhados nos permitem:
                    • Identificar quais leis lógicas são mais difíceis de aplicar
                    • Otimizar a interface do circuito interativo
                    • Melhorar a detecção de erros comuns
                    • Personalizar a experiência de aprendizado"""
        
        info_label = ctk.CTkLabel(main_frame, text=info_text, wraplength=750, justify="left")
        info_label.pack(pady=(10, 0))
        
        #Aguarda resposta
        root.wait_window(root)
        return self.result
    
    def _create_data_preview(self, summary: Dict[str, Any]) -> str:
        lines = []
        
        #Overview geral
        overview = summary.get("overview", {})
        lines.append("=" * 60)
        lines.append("📊 RESUMO GERAL")
        lines.append("=" * 60)
        lines.append(f"• Total de sessões: {overview.get('total_sessions', 0)}")
        lines.append(f"• Tempo total de uso: {overview.get('total_time_minutes', 0):.1f} minutos")
        lines.append(f"• Duração média por sessão: {overview.get('avg_session_duration', 0):.1f} minutos")
        lines.append(f"• Total de eventos registrados: {overview.get('total_events', 0)}")
        lines.append("")
        
        #Simplificação interativa com DADOS CORRIGIDOS
        simpl = summary.get("interactive_simplification", {})
        lines.append("=" * 60)
        lines.append("🔍 SIMPLIFICAÇÃO INTERATIVA")
        lines.append("=" * 60)
        
        total_sessions = simpl.get('total_sessions', 0)
        completed = simpl.get('expressions_completed', 0)
        abandoned = total_sessions - completed
        
        lines.append(f"• Sessões iniciadas: {total_sessions}")
        lines.append(f"• Sessões concluídas: {completed}")
        lines.append(f"• Sessões abandonadas: {abandoned}")
        
        #Taxa de conclusão CORRIGIDA
        completion_rate = simpl.get('completion_rate', 0) * 100
        lines.append(f"• Taxa de conclusão: {completion_rate:.1f}%")
        
        lines.append(f"• Total de passos realizados: {simpl.get('total_steps', 0)}")
        
        #Média de passos por sessão
        avg_steps = 0
        if total_sessions > 0:
            avg_steps = simpl.get('total_steps', 0) / total_sessions
        lines.append(f"• Média de passos/sessão: {avg_steps:.1f}")
        
        #Média de passos por sessão CONCLUÍDA
        avg_steps_completed = 0
        if completed > 0:
            avg_steps_completed = simpl.get('total_steps', 0) / completed
        lines.append(f"• Média de passos/conclusão: {avg_steps_completed:.1f}")
        
        lines.append(f"• Vezes que pulou: {simpl.get('total_skips', 0)}")
        lines.append(f"• Operações de desfazer: {simpl.get('total_undos', 0)}")
        
        #Leis mais usadas
        most_used = simpl.get('most_used_laws', {})
        if most_used:
            lines.append("\n📚 Leis mais aplicadas:")
            for law, count in list(most_used.items())[:5]:
                law_name = law.split('(')[0].strip()
                lines.append(f"  → {law_name}: {count}x")
        
        #Tentativas falhadas
        failed = simpl.get('failed_law_attempts', {})
        if failed:
            lines.append("\n⚠️ Leis com mais tentativas falhadas:")
            for law, count in list(failed.items())[:3]:
                law_name = law.split('(')[0].strip()
                lines.append(f"  → {law_name}: {count}x")
        
        lines.append("")
        
        #Circuito interativo
        circuit = summary.get("interactive_circuit", {})
        lines.append("=" * 60)
        lines.append("🔧 CIRCUITO INTERATIVO")
        lines.append("=" * 60)
        lines.append(f"• Sessões iniciadas: {circuit.get('total_sessions', 0)}")
        lines.append(f"• Componentes deletados: {circuit.get('total_deletions', 0)}")
        lines.append(f"• Tentativas de teste: {circuit.get('total_tests', 0)}")
        
        success_rate = circuit.get('success_rate', 0) * 100
        lines.append(f"• Taxa de sucesso: {success_rate:.1f}%")
        lines.append(f"• Operações de desfazer: {circuit.get('total_undos', 0)}")
        
        comp_usage = circuit.get('components_usage', {})
        if comp_usage:
            lines.append("\n🔌 Componentes mais utilizados:")
            for comp, count in list(comp_usage.items())[:5]:
                lines.append(f"  → {comp}: {count}x")
                
        lines.append("")
        
        #Resolução Direta (Adicionado)
        direct_res = summary.get("direct_resolution", {})
        lines.append("=" * 60)
        lines.append("⚡ RESOLUÇÃO DIRETA")
        lines.append("=" * 60)
        lines.append(f"• Expressões avaliadas: {direct_res.get('total_expressions_evaluated', 0)}")
        
        conv_modes = direct_res.get('conversion_modes_used', {})
        if conv_modes:
            lines.append("\n🔄 Modos de conversão:")
            for mode, count in list(conv_modes.items())[:3]:
                lines.append(f"  → {mode}: {count}x")
                
        features_used = summary.get("features_used", {})
        if features_used:
            lines.append("")
            lines.append("=" * 60)
            lines.append("🛠️ RECURSOS MAIS UTILIZADOS")
            lines.append("=" * 60)
            for feature, count in sorted(features_used.items(), key=lambda x: x[1], reverse=True)[:5]:
                lines.append(f"• {feature}: {count}x")
                
        #Equivalência
        equiv = summary.get("equivalence_checks", {})
        lines.append("=" * 60)
        lines.append("🔄 VERIFICAÇÃO DE EQUIVALÊNCIA")
        lines.append("=" * 60)
        lines.append(f"• Total de verificações: {equiv.get('total_checks', 0)}")
        
        if equiv.get('total_checks', 0) > 0:
            lines.append(f"• Pares equivalentes: {equiv.get('equivalent_found', 0)}")
            lines.append(f"• Pares não equivalentes: {equiv.get('non_equivalent_found', 0)}")
            
            equiv_rate = (equiv.get('equivalent_found', 0) / equiv.get('total_checks', 1)) * 100
            lines.append(f"• Taxa de equivalência: {equiv_rate:.1f}%")
            
            #Últimas verificações
            recent_checks = equiv.get('recent_checks', [])[:5]
            if recent_checks:
                lines.append("\n📋 Últimas verificações:")
                for i, check in enumerate(recent_checks, 1):
                    result_symbol = "✓ Equivalentes" if check.get('result') else "✗ Diferentes"
                    
                    if 'expr1_full' in check and 'expr2_full' in check:
                        expr1 = check['expr1_full'][:40] + "..." if len(check['expr1_full']) > 40 else check['expr1_full']
                        expr2 = check['expr2_full'][:40] + "..." if len(check['expr2_full']) > 40 else check['expr2_full']
                    else:
                        expr1 = check.get('expr1', 'N/A')
                        expr2 = check.get('expr2', 'N/A')
                    
                    lines.append(f"  {i}. {result_symbol}")
                    lines.append(f"     '{expr1}' vs '{expr2}'")
        else:
            lines.append("• Nenhuma verificação realizada ainda")
        
        lines.append("")
        lines.append("=" * 60)
        
        from datetime import datetime
        lines.append(f"📅 Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
        lines.append("=" * 60)
        
        return "\n".join(lines)

"""
Exemplo de análise dos dados detalhados coletados pelo sistema de logging.
Este script demonstra como extrair insights úteis dos dados para melhorar o LoZ Gates.
"""

import json
import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np

class LoZGatesDataAnalyzer:
    """Analisador de dados do LoZ Gates para extrair insights de uso."""
    
    def __init__(self, data_file_path: str):
        self.data_file = data_file_path
        self.sessions_data = []
        self.load_data()
    
    def load_data(self):
        """Carrega os dados do arquivo JSON."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.sessions_data = data.get('sessions', [])
            print(f"📊 Carregados {len(self.sessions_data)} sessões para análise")
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            self.sessions_data = []
    
    def analyze_simplification_patterns(self):
        """Analisa padrões na simplificação interativa."""
        print("\n=== ANÁLISE: SIMPLIFICAÇÃO INTERATIVA ===")
        
        all_laws = Counter()
        skip_rates = []
        completion_rates = []
        step_counts = []
        
        for session in self.sessions_data:
            simpl_data = session.get('interactive_simplification', {})
            
            # Leis mais usadas
            laws = simpl_data.get('laws_applied', {})
            all_laws.update(laws)
            
            # Taxa de pulos
            sessions_started = simpl_data.get('sessions_started', 0)
            skips = simpl_data.get('skips_used', 0)
            if sessions_started > 0:
                skip_rates.append(skips / sessions_started)
            
            # Taxa de conclusão
            completed = simpl_data.get('expressions_completed', 0)
            if sessions_started > 0:
                completion_rates.append(completed / sessions_started)
            
            # Passos por sessão
            total_steps = simpl_data.get('total_steps', 0)
            if sessions_started > 0:
                step_counts.append(total_steps / sessions_started)
        
        # Resultados
        print("🏆 Leis mais aplicadas:")
        for law, count in all_laws.most_common(5):
            print(f"   {law}: {count} aplicações")
        
        if skip_rates:
            avg_skip_rate = np.mean(skip_rates)
            print(f"⏭️ Taxa média de pulos: {avg_skip_rate:.2f} pulos/sessão")
        
        if completion_rates:
            avg_completion = np.mean(completion_rates)
            print(f"✅ Taxa média de conclusão: {avg_completion*100:.1f}%")
        
        if step_counts:
            avg_steps = np.mean(step_counts)
            print(f"🔢 Média de passos por sessão: {avg_steps:.1f}")
        
        return {
            'most_used_laws': dict(all_laws.most_common(10)),
            'avg_skip_rate': np.mean(skip_rates) if skip_rates else 0,
            'avg_completion_rate': np.mean(completion_rates) if completion_rates else 0,
            'avg_steps_per_session': np.mean(step_counts) if step_counts else 0
        }
    
    def analyze_circuit_building_behavior(self):
        """Analisa comportamento na construção de circuitos."""
        print("\n=== ANÁLISE: CIRCUITO INTERATIVO ===")
        
        component_usage = Counter()
        test_attempts = []
        success_rates = []
        deletion_rates = []
        undo_usage = []
        
        for session in self.sessions_data:
            circuit_data = session.get('interactive_circuit', {})
            
            # Uso de componentes
            components = circuit_data.get('components_added', {})
            component_usage.update(components)
            
            # Tentativas de teste
            tests = circuit_data.get('test_attempts', 0)
            sessions_started = circuit_data.get('sessions_started', 0)
            if sessions_started > 0 and tests > 0:
                test_attempts.append(tests / sessions_started)
            
            # Taxa de sucesso
            successful = circuit_data.get('successful_circuits', 0)
            if tests > 0:
                success_rates.append(successful / tests)
            
            # Taxa de deleção
            deletions = circuit_data.get('components_deleted', 0)
            total_components = sum(components.values())
            if total_components > 0:
                deletion_rates.append(deletions / total_components)
            
            # Uso de undo
            undos = circuit_data.get('undo_operations', 0)
            if sessions_started > 0:
                undo_usage.append(undos / sessions_started)
        
        # Resultados
        print("🔧 Componentes mais utilizados:")
        for component, count in component_usage.most_common(5):
            print(f"   {component}: {count} usos")
        
        if test_attempts:
            avg_tests = np.mean(test_attempts)
            print(f"🧪 Média de testes por sessão: {avg_tests:.1f}")
        
        if success_rates:
            avg_success = np.mean(success_rates)
            print(f"✅ Taxa média de sucesso: {avg_success*100:.1f}%")
        
        if deletion_rates:
            avg_deletions = np.mean(deletion_rates)
            print(f"🗑️ Taxa média de deleções: {avg_deletions*100:.1f}% dos componentes")
        
        if undo_usage:
            avg_undos = np.mean(undo_usage)
            print(f"↩️ Média de undos por sessão: {avg_undos:.1f}")
        
        return {
            'component_popularity': dict(component_usage.most_common()),
            'avg_tests_per_session': np.mean(test_attempts) if test_attempts else 0,
            'avg_success_rate': np.mean(success_rates) if success_rates else 0,
            'avg_deletion_rate': np.mean(deletion_rates) if deletion_rates else 0,
            'avg_undo_usage': np.mean(undo_usage) if undo_usage else 0
        }
    
    def analyze_equivalence_patterns(self):
        """Analisa padrões nas verificações de equivalência."""
        print("\n=== ANÁLISE: VERIFICAÇÃO DE EQUIVALÊNCIA ===")
        
        all_checks = []
        complexity_patterns = []
        
        for session in self.sessions_data:
            equiv_data = session.get('equivalence_analysis', {})
            checks = equiv_data.get('expression_pairs', [])
            all_checks.extend(checks)
        
        if not all_checks:
            print("⚠️ Nenhuma verificação de equivalência encontrada")
            return {}
        
        # Análise dos resultados
        total_checks = len(all_checks)
        equivalent_count = sum(1 for check in all_checks if check.get('result'))
        non_equivalent_count = total_checks - equivalent_count
        
        # Análise de complexidade
        for check in all_checks:
            expr1_len = check.get('expr1_length', 0)
            expr2_len = check.get('expr2_length', 0)
            complexity_diff = abs(expr1_len - expr2_len)
            complexity_patterns.append({
                'diff': complexity_diff,
                'result': check.get('result'),
                'avg_length': (expr1_len + expr2_len) / 2
            })
        
        # Sequência temporal de verificações
        recent_pattern = []
        for check in all_checks[-10:]:  # Últimas 10 verificações
            recent_pattern.append("✓" if check.get('result') else "✗")
        
        print(f"📊 Total de verificações: {total_checks}")
        print(f"✅ Equivalentes: {equivalent_count} ({equivalent_count/total_checks*100:.1f}%)")
        print(f"❌ Não equivalentes: {non_equivalent_count} ({non_equivalent_count/total_checks*100:.1f}%)")
        
        if recent_pattern:
            print(f"🔄 Padrão recente: {' '.join(recent_pattern)}")
        
        # Análise de complexidade
        if complexity_patterns:
            avg_complexity_diff = np.mean([p['diff'] for p in complexity_patterns])
            print(f"📏 Diferença média de complexidade: {avg_complexity_diff:.1f} caracteres")
        
        return {
            'total_checks': total_checks,
            'equivalent_rate': equivalent_count / total_checks if total_checks > 0 else 0,
            'avg_complexity_difference': np.mean([p['diff'] for p in complexity_patterns]) if complexity_patterns else 0,
            'recent_pattern': recent_pattern
        }
    
    def analyze_expression_complexity_trends(self):
        """Analisa tendências de complexidade das expressões."""
        print("\n=== ANÁLISE: COMPLEXIDADE DAS EXPRESSÕES ===")
        
        variable_counts = Counter()
        expression_lengths = Counter()
        operator_usage = {'AND': 0, 'OR': 0, 'NOT': 0}
        
        for session in self.sessions_data:
            patterns = session.get('expression_patterns', {})
            
            # Contagem de variáveis
            var_counts = patterns.get('variable_counts', {})
            for count, freq in var_counts.items():
                variable_counts[int(count)] += freq
            
            # Comprimentos de expressão
            lengths = patterns.get('expression_lengths', {})
            for length, freq in lengths.items():
                expression_lengths[int(length)] += freq
            
            # Uso de operadores
            ops = patterns.get('operator_usage', {})
            for op in operator_usage:
                operator_usage[op] += ops.get(op, 0)
        
        # Resultados
        print("🔢 Distribuição de variáveis por expressão:")
        for var_count in sorted(variable_counts.keys()):
            freq = variable_counts[var_count]
            print(f"   {var_count} variáveis: {freq} expressões")
        
        print("📏 Distribuição de tamanhos de expressão:")
        for length in sorted(expression_lengths.keys())[:10]:  # Top 10
            freq = expression_lengths[length]
            print(f"   {length} caracteres: {freq} expressões")
        
        print("⚡ Preferência de operadores:")
        total_ops = sum(operator_usage.values())
        if total_ops > 0:
            for op, count in operator_usage.items():
                percentage = (count / total_ops) * 100
                print(f"   {op}: {count} usos ({percentage:.1f}%)")
        
        return {
            'variable_distribution': dict(variable_counts),
            'length_distribution': dict(expression_lengths),
            'operator_preferences': operator_usage
        }
    
    def analyze_error_patterns(self):
        """Analisa padrões de erros encontrados pelos usuários."""
        print("\n=== ANÁLISE: PADRÕES DE ERROS ===")
        
        total_errors = 0
        sessions_with_errors = 0
        error_types = Counter()
        
        for session in self.sessions_data:
            session_stats = session.get('session_stats', {})
            errors_in_session = session_stats.get('errors_encountered', 0)
            
            total_errors += errors_in_session
            if errors_in_session > 0:
                sessions_with_errors += 1
            
            # Analisa eventos de erro
            events = session.get('events', [])
            for event in events:
                if event.get('type') == 'error_occurred':
                    error_type = event.get('data', {}).get('error_type', 'unknown')
                    error_types[error_type] += 1
        
        total_sessions = len(self.sessions_data)
        
        print(f"⚠️ Total de erros: {total_errors}")
        print(f"📊 Sessões com erros: {sessions_with_errors}/{total_sessions} ({sessions_with_errors/total_sessions*100:.1f}%)")
        
        if error_types:
            print("🔍 Tipos de erros mais comuns:")
            for error_type, count in error_types.most_common(5):
                print(f"   {error_type}: {count} ocorrências")
        
        return {
            'total_errors': total_errors,
            'sessions_with_errors_rate': sessions_with_errors / total_sessions if total_sessions > 0 else 0,
            'common_error_types': dict(error_types.most_common(10))
        }
    
    def analyze_user_engagement(self):
        """Analisa padrões de engajamento dos usuários."""
        print("\n=== ANÁLISE: ENGAJAMENTO DO USUÁRIO ===")
        
        session_durations = []
        events_per_session = []
        feature_usage = Counter()
        
        for session in self.sessions_data:
            duration = session.get('duration_seconds', 0)
            if duration > 0:
                session_durations.append(duration / 60)  # Converte para minutos
            
            events_count = session.get('events_count', 0)
            if events_count > 0:
                events_per_session.append(events_count)
            
            # Conta uso de features
            events = session.get('events', [])
            for event in events:
                if event.get('type') == 'feature_used':
                    feature = event.get('data', {}).get('feature', 'unknown')
                    feature_usage[feature] += 1
        
        # Resultados
        if session_durations:
            avg_duration = np.mean(session_durations)
            median_duration = np.median(session_durations)
            print(f"⏱️ Duração média de sessão: {avg_duration:.1f} minutos")
            print(f"⏱️ Duração mediana: {median_duration:.1f} minutos")
        
        if events_per_session:
            avg_events = np.mean(events_per_session)
            print(f"🎯 Média de eventos por sessão: {avg_events:.1f}")
        
        print("🏆 Features mais utilizadas:")
        for feature, count in feature_usage.most_common(5):
            print(f"   {feature}: {count} usos")
        
        return {
            'avg_session_duration_minutes': np.mean(session_durations) if session_durations else 0,
            'median_session_duration_minutes': np.median(session_durations) if session_durations else 0,
            'avg_events_per_session': np.mean(events_per_session) if events_per_session else 0,
            'most_used_features': dict(feature_usage.most_common(10))
        }
    
    def generate_comprehensive_report(self):
        """Gera relatório completo de análise."""
        print("🚀 Gerando relatório completo de análise do LoZ Gates...")
        print("=" * 60)
        
        report = {
            'analysis_date': datetime.now().isoformat(),
            'total_sessions_analyzed': len(self.sessions_data),
            'simplification_analysis': self.analyze_simplification_patterns(),
            'circuit_analysis': self.analyze_circuit_building_behavior(),
            'equivalence_analysis': self.analyze_equivalence_patterns(),
            'expression_complexity': self.analyze_expression_complexity_trends(),
            'error_patterns': self.analyze_error_patterns(),
            'user_engagement': self.analyze_user_engagement()
        }
        
        print("\n" + "=" * 60)
        print("📋 RESUMO EXECUTIVO:")
        print(f"• Total de sessões analisadas: {report['total_sessions_analyzed']}")
        
        simpl = report['simplification_analysis']
        if simpl:
            print(f"• Taxa de conclusão na simplificação: {simpl.get('avg_completion_rate', 0)*100:.1f}%")
            print(f"• Passos médios por simplificação: {simpl.get('avg_steps_per_session', 0):.1f}")
        
        circuit = report['circuit_analysis']
        if circuit:
            print(f"• Taxa de sucesso no circuito: {circuit.get('avg_success_rate', 0)*100:.1f}%")
            print(f"• Testes médios por circuito: {circuit.get('avg_tests_per_session', 0):.1f}")
        
        engagement = report['user_engagement']
        if engagement:
            print(f"• Duração média de sessão: {engagement.get('avg_session_duration_minutes', 0):.1f} min")
        
        errors = report['error_patterns']
        if errors:
            print(f"• Taxa de sessões com erro: {errors.get('sessions_with_errors_rate', 0)*100:.1f}%")
        
        return report
    
    def save_report_to_file(self, report, filename="loz_gates_analysis_report.json"):
        """Salva o relatório em arquivo JSON."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"💾 Relatório salvo em: {filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")

# Exemplo de uso
if __name__ == "__main__":
    # Inicializa o analisador
    analyzer = LoZGatesDataAnalyzer("user_activity_detailed.json")
    
    # Gera análise completa
    report = analyzer.generate_comprehensive_report()
    
    # Salva relatório
    analyzer.save_report_to_file(report)
    
    # Exemplos de insights específicos que você pode extrair:
    print("\n🎯 INSIGHTS ESPECÍFICOS PARA MELHORIA:")
    
    # 1. Leis mais difíceis
    simpl = report.get('simplification_analysis', {})
    laws = simpl.get('most_used_laws', {})
    if laws:
        least_used = sorted(laws.items(), key=lambda x: x[1])[:3]
        print(f"📚 Leis menos utilizadas (podem precisar de mais explicação):")
        for law, count in least_used:
            print(f"   • {law}: apenas {count} usos")
    
    # 2. Componentes problemáticos no circuito
    circuit = report.get('circuit_analysis', {})
    deletion_rate = circuit.get('avg_deletion_rate', 0)
    if deletion_rate > 0.3:  # Se mais de 30% dos componentes são deletados
        print(f"⚠️ Alta taxa de deleção ({deletion_rate*100:.1f}%) sugere interface confusa")
    
    # 3. Padrões de erro
    errors = report.get('error_patterns', {})
    common_errors = errors.get('common_error_types', {})
    if common_errors:
        print("🔧 Erros mais comuns que precisam ser corrigidos:")
        for error_type, count in list(common_errors.items())[:3]:
            print(f"   • {error_type}: {count} ocorrências")
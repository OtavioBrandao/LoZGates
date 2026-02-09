import json
from collections import Counter
from datetime import datetime
import numpy as np

class LoZGatesDataAnalyzer:
    def __init__(self, data_file_path: str):
        self.data_file = data_file_path
        self.sessions_data = []
        self.load_data()

    def load_data(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.sessions_data = data.get('sessions', [])
            print(f"📊 Carregados {len(self.sessions_data)} sessões para análise")
        except FileNotFoundError:
            print(f"❌ Erro: Arquivo '{self.data_file}' não encontrado. Gere alguns logs primeiro.")
            self.sessions_data = []
        except json.JSONDecodeError:
            print(f"❌ Erro: O arquivo '{self.data_file}' está corrompido ou em um formato JSON inválido.")
            self.sessions_data = []
        except Exception as e:
            print(f"❌ Erro inesperado ao carregar dados: {e}")
            self.sessions_data = []

    def analyze_simplification_patterns(self):
        if not self.sessions_data: return {}
        print("\n=== ANÁLISE: SIMPLIFICAÇÃO INTERATIVA ===")

        all_laws = Counter()
        skip_rates = []
        completion_rates = []
        step_counts = []

        for session in self.sessions_data:
            simpl_data = session.get('interactive_simplification', {})
            laws = simpl_data.get('laws_applied', {})
            all_laws.update(laws)

            sessions_started = simpl_data.get('sessions_started', 0)
            if sessions_started > 0:
                skips = simpl_data.get('skips_used', 0)
                skip_rates.append(skips / sessions_started)
                
                completed = simpl_data.get('expressions_completed', 0)
                completion_rates.append(completed / sessions_started)
                
                total_steps = simpl_data.get('total_steps', 0)
                step_counts.append(total_steps / sessions_started)
        
        return {
            'most_used_laws': dict(all_laws.most_common(10)),
            'avg_skip_rate': np.mean(skip_rates) if skip_rates else 0,
            'avg_completion_rate': np.mean(completion_rates) if completion_rates else 0,
            'avg_steps_per_session': np.mean(step_counts) if step_counts else 0
        }

    def analyze_circuit_building_behavior(self):
        if not self.sessions_data: return {}
        print("\n=== ANÁLISE: CIRCUITO INTERATIVO ===")
        
        component_usage = Counter()
        test_attempts, success_rates, deletion_rates, undo_usage = [], [], [], []

        for session in self.sessions_data:
            circuit_data = session.get('interactive_circuit', {})
            components = circuit_data.get('components_added', {})
            component_usage.update(components)

            sessions_started = circuit_data.get('sessions_started', 0)
            if sessions_started > 0:
                tests = circuit_data.get('test_attempts', 0)
                if tests > 0:
                    test_attempts.append(tests / sessions_started)
                    successful = circuit_data.get('successful_circuits', 0)
                    success_rates.append(successful / tests)

                total_components = sum(components.values())
                if total_components > 0:
                    deletions = circuit_data.get('components_deleted', 0)
                    deletion_rates.append(deletions / total_components)

                undos = circuit_data.get('undo_operations', 0)
                undo_usage.append(undos / sessions_started)
        
        return {
            'component_popularity': dict(component_usage.most_common()),
            'avg_tests_per_session': np.mean(test_attempts) if test_attempts else 0,
            'avg_success_rate': np.mean(success_rates) if success_rates else 0,
            'avg_deletion_rate': np.mean(deletion_rates) if deletion_rates else 0,
            'avg_undo_usage': np.mean(undo_usage) if undo_usage else 0
        }
        
    def analyze_equivalence_patterns(self):
        if not self.sessions_data: 
            return {}
        
        print("\n=== ANÁLISE: VERIFICAÇÃO DE EQUIVALÊNCIA ===")
        all_checks = [check for s in self.sessions_data for check in s.get('equivalence_analysis', {}).get('expression_pairs', [])]
        
        if not all_checks: 
            return {}
        
        total_checks = len(all_checks)
        equivalent_count = sum(1 for c in all_checks if c.get('result'))
        return {'total_checks': total_checks, 'equivalent_rate': equivalent_count / total_checks}

    def analyze_expression_complexity_trends(self):
        if not self.sessions_data: 
            return {}
        
        print("\n=== ANÁLISE: COMPLEXIDADE DAS EXPRESSÕES ===")
        variable_counts, expression_lengths, operator_usage = Counter(), Counter(), Counter()
        
        for session in self.sessions_data:
            patterns = session.get('expression_patterns', {})
            
            for count, freq in patterns.get('variable_counts', {}).items(): 
                variable_counts[int(count)] += freq
                
            for length, freq in patterns.get('expression_lengths', {}).items(): 
                expression_lengths[int(length)] += freq
                
            operator_usage.update(patterns.get('operator_usage', {}))
        return {'variable_distribution': dict(variable_counts), 'length_distribution': dict(expression_lengths), 'operator_preferences': dict(operator_usage)}

    def analyze_error_patterns(self):
        if not self.sessions_data:
            return {}
        
        print("\n=== ANÁLISE: PADRÕES DE ERROS ===")
        total_errors = sum(s.get('session_stats', {}).get('errors_encountered', 0) for s in self.sessions_data)
        sessions_with_errors = sum(1 for s in self.sessions_data if s.get('session_stats', {}).get('errors_encountered', 0) > 0)
        error_types = Counter(e.get('data', {}).get('error_type', 'unknown') for s in self.sessions_data for e in s.get('events', []) if e.get('type') == 'error_occurred')
        
        return {'total_errors': total_errors, 'sessions_with_errors_rate': sessions_with_errors / len(self.sessions_data), 'common_error_types': dict(error_types.most_common(10))}

    def analyze_user_engagement(self):
        if not self.sessions_data:
            return {}
        
        print("\n=== ANÁLISE: ENGAJAMENTO DO USUÁRIO ===")
        session_durations = [s.get('duration_seconds', 0) / 60 for s in self.sessions_data if s.get('duration_seconds', 0) > 0]
        events_per_session = [s.get('events_count', 0) for s in self.sessions_data if s.get('events_count', 0) > 0]
        feature_usage = Counter(e.get('data', {}).get('feature', 'unknown') for s in self.sessions_data for e in s.get('events', []) if e.get('type') == 'feature_used')
        
        return {'avg_session_duration_minutes': np.mean(session_durations) if session_durations else 0, 'median_session_duration_minutes': np.median(session_durations) if session_durations else 0, 'avg_events_per_session': np.mean(events_per_session) if events_per_session else 0, 'most_used_features': dict(feature_usage.most_common(10))}

    def generate_comprehensive_report(self):
        if not self.sessions_data:
            print("Nenhum dado de sessão para analisar.")
            return None
        
        print("🚀 Gerando relatório completo de análise do LoZ Gates...")
        
        return {
            'analysis_date': datetime.now().isoformat(),
            'total_sessions_analyzed': len(self.sessions_data),
            'simplification_analysis': self.analyze_simplification_patterns(),
            'circuit_analysis': self.analyze_circuit_building_behavior(),
            'equivalence_analysis': self.analyze_equivalence_patterns(),
            'expression_complexity': self.analyze_expression_complexity_trends(),
            'error_patterns': self.analyze_error_patterns(),
            'user_engagement': self.analyze_user_engagement()
        }

    def save_report_to_file(self, report, filename="loz_gates_analysis_report.json"):
        if not report: return
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"💾 Relatório salvo em: {filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar relatório: {e}")

    def generate_html_report(self, report, filename="analysis_report.html"):
        if not report:
            return

        simpl = report.get('simplification_analysis', {})
        circuit = report.get('circuit_analysis', {})
        equiv = report.get('equivalence_analysis', {})
        complexity = report.get('expression_complexity', {})
        errors = report.get('error_patterns', {})
        engagement = report.get('user_engagement', {})

        # CSS moderno e responsivo
        html_style = """
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
                line-height: 1.6;
            }

            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
                animation: fadeIn 0.5s ease-in;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }

            .header h1 {
                font-size: 2.8em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }

            .header .subtitle {
                font-size: 1.2em;
                opacity: 0.95;
                margin-bottom: 15px;
            }

            .timestamp {
                font-size: 0.95em;
                opacity: 0.85;
                font-style: italic;
            }

            .content {
                padding: 30px;
            }

            /* Cards de Estatísticas */
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 25px;
                margin-bottom: 40px;
            }

            .stat-card {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 30px;
                border-radius: 15px;
                color: white;
                text-align: center;
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                cursor: pointer;
            }

            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.25);
            }

            .stat-card:nth-child(2) {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            }

            .stat-card:nth-child(3) {
                background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            }

            .stat-card:nth-child(4) {
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            }

            .stat-number {
                font-size: 3em;
                font-weight: bold;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }

            .stat-label {
                font-size: 1.15em;
                opacity: 0.95;
                text-transform: uppercase;
                letter-spacing: 1px;
            }

            /* Seções */
            .section {
                margin: 40px 0;
                padding: 30px;
                background: #f8f9fa;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                transition: transform 0.3s ease;
            }

            .section:hover {
                transform: translateX(5px);
            }

            .section h2 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 15px;
                margin-bottom: 25px;
                font-size: 2em;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .section h3 {
                color: #34495e;
                margin: 25px 0 15px;
                font-size: 1.4em;
            }

            /* Info Rows */
            .info-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 12px 0;
                padding: 15px 20px;
                background: white;
                border-radius: 10px;
                border-left: 4px solid #3498db;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                transition: all 0.3s ease;
            }

            .info-row:hover {
                transform: translateX(5px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }

            .info-row strong {
                color: #2c3e50;
                font-size: 1.1em;
            }

            /* Ranking Items */
            .ranking-item {
                background: white;
                margin: 12px 0;
                padding: 18px 25px;
                border-radius: 10px;
                border-left: 5px solid #f39c12;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 3px 10px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
            }

            .ranking-item:hover {
                transform: translateX(8px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.15);
                border-left-color: #e67e22;
            }

            .ranking-item:nth-child(1) { border-left-color: #e74c3c; }
            .ranking-item:nth-child(2) { border-left-color: #e67e22; }
            .ranking-item:nth-child(3) { border-left-color: #f39c12; }

            .ranking-item strong {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.95em;
            }

            /* Charts Container */
            .chart-container {
                background: white;
                padding: 25px;
                border-radius: 12px;
                margin: 20px 0;
                box-shadow: 0 3px 10px rgba(0,0,0,0.08);
            }

            /* Progress Bars */
            .progress-bar {
                width: 100%;
                height: 30px;
                background: #ecf0f1;
                border-radius: 15px;
                overflow: hidden;
                margin: 10px 0;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
            }

            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-right: 15px;
                color: white;
                font-weight: bold;
                transition: width 1s ease;
            }

            /* Tabs */
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                border-bottom: 2px solid #ecf0f1;
            }

            .tab {
                padding: 12px 25px;
                background: transparent;
                border: none;
                cursor: pointer;
                font-size: 1em;
                color: #7f8c8d;
                transition: all 0.3s ease;
                border-bottom: 3px solid transparent;
            }

            .tab:hover {
                color: #3498db;
            }

            .tab.active {
                color: #3498db;
                border-bottom-color: #3498db;
            }

            .tab-content {
                display: none;
            }

            .tab-content.active {
                display: block;
                animation: fadeIn 0.3s ease;
            }

            /* Footer */
            .footer {
                background: #2c3e50;
                color: white;
                padding: 25px;
                text-align: center;
            }

            /* Responsive */
            @media (max-width: 768px) {
                .stats-grid {
                    grid-template-columns: 1fr;
                }
                
                .header h1 {
                    font-size: 2em;
                }
                
                .stat-number {
                    font-size: 2.5em;
                }
            }

            /* Print Styles */
            @media print {
                body {
                    background: white;
                }
                
                .container {
                    box-shadow: none;
                }
                
                .stat-card:hover, .section:hover {
                    transform: none;
                }
            }
        </style>
        """

        # JavaScript para interatividade
        html_script = """
        <script>
            // Tabs functionality
            function openTab(evt, tabName) {
                const tabContents = document.getElementsByClassName("tab-content");
                for (let content of tabContents) {
                    content.classList.remove("active");
                }
                
                const tabs = document.getElementsByClassName("tab");
                for (let tab of tabs) {
                    tab.classList.remove("active");
                }
                
                document.getElementById(tabName).classList.add("active");
                evt.currentTarget.classList.add("active");
            }

            // Animate numbers on load
            window.addEventListener('load', () => {
                const statNumbers = document.querySelectorAll('.stat-number');
                statNumbers.forEach(num => {
                    const finalValue = parseFloat(num.textContent);
                    let currentValue = 0;
                    const increment = finalValue / 50;
                    const timer = setInterval(() => {
                        currentValue += increment;
                        if (currentValue >= finalValue) {
                            num.textContent = num.dataset.suffix 
                                ? finalValue.toFixed(1) + num.dataset.suffix 
                                : Math.round(finalValue);
                            clearInterval(timer);
                        } else {
                            num.textContent = num.dataset.suffix 
                                ? currentValue.toFixed(1) + num.dataset.suffix 
                                : Math.round(currentValue);
                        }
                    }, 20);
                });

                // Animate progress bars
                const progressBars = document.querySelectorAll('.progress-fill');
                progressBars.forEach(bar => {
                    const width = bar.style.width;
                    bar.style.width = '0%';
                    setTimeout(() => {
                        bar.style.width = width;
                    }, 100);
                });
            });

            // Print functionality
            function printReport() {
                window.print();
            }

            // Export to JSON
            function exportToJSON() {
                const report = {};
                const dataStr = JSON.stringify(report, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                const url = URL.createObjectURL(dataBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'loz_gates_report.json';
                link.click();
            }
        </script>
        """

        # Constrói o HTML
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Relatório de Análise - LoZ Gates</title>
            {html_style}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Relatório de Análise LoZ Gates</h1>
                    <p class="subtitle">Análise Detalhada da Atividade dos Usuários</p>
                    <p class="timestamp">Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
                </div>

                <div class="content">
                    <!-- Stats Cards -->
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number" data-suffix="">{report.get('total_sessions_analyzed', 0)}</div>
                            <div class="stat-label">Sessões Analisadas</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" data-suffix=" min">{engagement.get('avg_session_duration_minutes', 0)}</div>
                            <div class="stat-label">Duração Média</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" data-suffix="%">{simpl.get('avg_completion_rate', 0)*100}</div>
                            <div class="stat-label">Taxa de Conclusão</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" data-suffix="%">{circuit.get('avg_success_rate', 0)*100}</div>
                            <div class="stat-label">Taxa de Sucesso</div>
                        </div>
                    </div>

                    <!-- Tabs -->
                    <div class="tabs">
                        <button class="tab active" onclick="openTab(event, 'simplification')">🔍 Simplificação</button>
                        <button class="tab" onclick="openTab(event, 'circuit')">🔧 Circuito</button>
                        <button class="tab" onclick="openTab(event, 'complexity')">📈 Complexidade</button>
                        <button class="tab" onclick="openTab(event, 'errors')">⚠️ Erros</button>
                    </div>

                    <!-- Tab: Simplificação -->
                    <div id="simplification" class="tab-content active">
                        <div class="section">
                            <h2>🔍 Análise de Simplificação Interativa</h2>
                            
                            <div class="info-row">
                                <span>Taxa Média de Conclusão:</span>
                                <strong>{simpl.get('avg_completion_rate', 0)*100:.1f}%</strong>
                            </div>
                            
                            <div class="chart-container">
                                <h3>Taxa de Conclusão</h3>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: {simpl.get('avg_completion_rate', 0)*100}%">
                                        {simpl.get('avg_completion_rate', 0)*100:.1f}%
                                    </div>
                                </div>
                            </div>

                            <div class="info-row">
                                <span>Média de Passos por Sessão:</span>
                                <strong>{simpl.get('avg_steps_per_session', 0):.1f}</strong>
                            </div>

                            <h3>🏆 Leis Mais Utilizadas</h3>
                            {''.join([f'''<div class="ranking-item">
                                <span>{law.split("(")[0].strip()}</span>
                                <strong>{count} aplicações</strong>
                            </div>''' for law, count in list(simpl.get('most_used_laws', {}).items())[:10]])}
                        </div>
                    </div>

                    <!-- Tab: Circuito -->
                    <div id="circuit" class="tab-content">
                        <div class="section">
                            <h2>🔧 Análise de Construção de Circuitos</h2>
                            
                            <div class="chart-container">
                                <h3>Taxa de Sucesso</h3>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: {circuit.get('avg_success_rate', 0)*100}%">
                                        {circuit.get('avg_success_rate', 0)*100:.1f}%
                                    </div>
                                </div>
                            </div>

                            <div class="info-row">
                                <span>Média de Testes por Sessão:</span>
                                <strong>{circuit.get('avg_tests_per_session', 0):.1f}</strong>
                            </div>

                            <div class="info-row">
                                <span>Taxa de Deleções:</span>
                                <strong>{circuit.get('avg_deletion_rate', 0)*100:.1f}%</strong>
                            </div>

                            <h3>🎯 Componentes Mais Populares</h3>
                            {''.join([f'''<div class="ranking-item">
                                <span>{comp.upper()}</span>
                                <strong>{count} usos</strong>
                            </div>''' for comp, count in list(circuit.get('component_popularity', {}).items())[:10]])}
                        </div>
                    </div>

                    <!-- Tab: Complexidade -->
                    <div id="complexity" class="tab-content">
                        <div class="section">
                            <h2>📈 Análise de Complexidade das Expressões</h2>
                            
                            <h3>Distribuição de Variáveis</h3>
                            {''.join([f'''<div class="info-row">
                                <span>{var} variáveis:</span>
                                <strong>{count} expressões</strong>
                            </div>''' for var, count in sorted(complexity.get('variable_distribution', {}).items())])}

                            <h3>Uso de Operadores</h3>
                            <div class="chart-container">
                                {''.join([f'''<div style="margin: 15px 0;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                        <span>{op}</span>
                                        <strong>{count} usos</strong>
                                    </div>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: {count/max(complexity.get('operator_preferences', {}).values(), default=1)*100}%"></div>
                                    </div>
                                </div>''' for op, count in complexity.get('operator_preferences', {}).items()])}
                            </div>
                        </div>
                    </div>

                    <!-- Tab: Erros -->
                    <div id="errors" class="tab-content">
                        <div class="section">
                            <h2>⚠️ Análise de Padrões de Erros</h2>
                            
                            <div class="info-row">
                                <span>Total de Erros:</span>
                                <strong>{errors.get('total_errors', 0)}</strong>
                            </div>

                            <div class="chart-container">
                                <h3>Taxa de Sessões com Erros</h3>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: {errors.get('sessions_with_errors_rate', 0)*100}%; background: linear-gradient(90deg, #e74c3c 0%, #c0392b 100%);">
                                        {errors.get('sessions_with_errors_rate', 0)*100:.1f}%
                                    </div>
                                </div>
                            </div>

                            <h3>Tipos de Erro Mais Comuns</h3>
                            {''.join([f'''<div class="ranking-item">
                                <span>{err}</span>
                                <strong>{count} ocorrências</strong>
                            </div>''' for err, count in list(errors.get('common_error_types', {}).items())[:10]])}
                        </div>
                    </div>

                    <!-- Engagement Section -->
                    <div class="section">
                        <h2>📊 Engajamento do Usuário</h2>
                        
                        <div class="info-row">
                            <span>Duração Média da Sessão:</span>
                            <strong>{engagement.get('avg_session_duration_minutes', 0):.1f} minutos</strong>
                        </div>

                        <div class="info-row">
                            <span>Duração Mediana:</span>
                            <strong>{engagement.get('median_session_duration_minutes', 0):.1f} minutos</strong>
                        </div>

                        <div class="info-row">
                            <span>Eventos por Sessão:</span>
                            <strong>{engagement.get('avg_events_per_session', 0):.1f}</strong>
                        </div>

                        <h3>🎯 Funcionalidades Mais Usadas</h3>
                        {''.join([f'''<div class="ranking-item">
                            <span>{feature.replace('_', ' ').title()}</span>
                            <strong>{count} usos</strong>
                        </div>''' for feature, count in list(engagement.get('most_used_features', {}).items())[:10]])}
                    </div>
                </div>

                <div class="footer">
                    <p>LoZ Gates - Sistema de Análise de Dados | © 2024 UFAL</p>
                    <p style="margin-top: 10px;">
                        <button onclick="printReport()" style="padding: 8px 16px; margin: 0 5px; cursor: pointer; background: white; color: #2c3e50; border: none; border-radius: 5px;">🖨️ Imprimir</button>
                        <button onclick="exportToJSON()" style="padding: 8px 16px; margin: 0 5px; cursor: pointer; background: white; color: #2c3e50; border: none; border-radius: 5px;">💾 Exportar JSON</button>
                    </p>
                </div>
            </div>
            {html_script}
        </body>
        </html>
        """

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"📄 Relatório HTML aprimorado salvo em: {filename}")
        except Exception as e:
            print(f"❌ Erro ao salvar relatório HTML: {e}")
            
if __name__ == "__main__":
    analyzer = LoZGatesDataAnalyzer("user_activity_detailed.json")
    report = analyzer.generate_comprehensive_report()
    analyzer.save_report_to_file(report)
    analyzer.generate_html_report(report)
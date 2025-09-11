
from BackEnd.register_data import load_log
from datetime import datetime


def generate_html_log(log_path="logs.json", output_path="relatorio_estatisticas.html"):
    """Gera um relatório HTML com as estatísticas dos logs"""
    
    logs = load_log(log_path)

    if not logs["expressoes"]:
        print("Nenhum dado encontrado para gerar relatório.")
        return
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório de Estatísticas - Simplificador Lógico</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }}
            h1 {{
                text-align: center;
                color: #2c3e50;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }}
            .subtitle {{
                text-align: center;
                color: #7f8c8d;
                font-size: 1.2em;
                margin-bottom: 30px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 20px;
                border-radius: 10px;
                color: white;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }}
            .stat-number {{
                font-size: 2.5em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .stat-label {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            .section {{
                margin: 40px 0;
                padding: 25px;
                background: #f8f9fa;
                border-radius: 10px;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
            }}
            .section h2 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                font-size: 1.8em;
            }}
            .expression-card {{
                background: white;
                margin: 15px 0;
                padding: 20px;
                border-radius: 8px;
                border-left: 5px solid #3498db;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .expression-title {{
                font-family: 'Courier New', monospace;
                font-size: 1.3em;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
                background: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
            }}
            .laws-used {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 15px 0;
            }}
            .law-badge {{
                background: #3498db;
                color: white;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: bold;
            }}
            .success {{
                background: #27ae60;
            }}
            .failure {{
                background: #e74c3c;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                margin: 8px 0;
                padding: 8px;
                background: #f8f9fa;
                border-radius: 5px;
            }}
            .progress-bar {{
                background: #ecf0f1;
                border-radius: 10px;
                overflow: hidden;
                height: 20px;
                margin: 10px 0;
            }}
            .progress-fill {{
                background: linear-gradient(90deg, #27ae60, #2ecc71);
                height: 100%;
                transition: width 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 0.8em;
            }}
            .timestamp {{
                font-size: 0.9em;
                color: #7f8c8d;
                font-style: italic;
            }}
            .ranking {{
                counter-reset: ranking;
            }}
            .ranking-item {{
                counter-increment: ranking;
                background: white;
                margin: 10px 0;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #f39c12;
                display: flex;
                align-items: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .ranking-item::before {{
                content: counter(ranking) "º";
                background: #f39c12;
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                margin-right: 15px;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Relatório de Estatísticas</h1>
            <p class="subtitle">Simplificador de Expressões Lógicas - Dados de Uso</p>
            <p class="timestamp">Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(logs["expressoes"])}</div>
                    <div class="stat-label">Expressões Testadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(expr["tentativas_totais"] for expr in logs["expressoes"].values())}</div>
                    <div class="stat-label">Tentativas Totais</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(expr["sucessos_totais"] for expr in logs["expressoes"].values())}</div>
                    <div class="stat-label">Sucessos Totais</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(len(expr["sessoes"]) for expr in logs["expressoes"].values())}</div>
                    <div class="stat-label">Sessões de Uso</div>
                </div>
            </div>
    """
    
    # Seção de expressões mais tentadas
    expressoes_ordenadas = sorted(logs["expressoes"].items(), 
                                key=lambda x: x[1]["tentativas_totais"], reverse=True)
    
    html_content += """
            <div class="section">
                <h2>🏆 Expressões Mais Tentadas</h2>
                <div class="ranking">
    """
    
    for i, (expr, dados) in enumerate(expressoes_ordenadas[:10]):  # Top 10
        taxa_sucesso = (dados["sucessos_totais"] / dados["tentativas_totais"] * 100) if dados["tentativas_totais"] > 0 else 0
        tempo_medio = dados.get("tempo_medio", 0)
        
        html_content += f"""
                    <div class="ranking-item">
                        <div style="flex-grow: 1;">
                            <div class="expression-title">{expr}</div>
                            <div class="info-row">
                                <span>Tentativas:</span>
                                <strong>{dados["tentativas_totais"]}</strong>
                            </div>
                            <div class="info-row">
                                <span>Sucessos:</span>
                                <strong>{dados["sucessos_totais"]}</strong>
                            </div>
                            <div class="info-row">
                                <span>Taxa de Sucesso:</span>
                                <strong>{taxa_sucesso:.1f}%</strong>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {taxa_sucesso}%">
                                    {taxa_sucesso:.1f}%
                                </div>
                            </div>
                            <div class="info-row">
                                <span>Tempo Médio:</span>
                                <strong>{tempo_medio:.2f}s</strong>
                            </div>
                        </div>
                    </div>
        """
    
    html_content += """
                </div>
            </div>
    """
    
    # Seção de leis mais usadas
    if "leis_mais_usadas" in logs.get("estatisticas_gerais", {}):
        leis_ordenadas = sorted(logs["estatisticas_gerais"]["leis_mais_usadas"].items(), 
                              key=lambda x: x[1], reverse=True)
        
        html_content += """
            <div class="section">
                <h2>⚖️ Leis Mais Utilizadas</h2>
                <div class="ranking">
        """
        
        for lei, usos in leis_ordenadas:
            html_content += f"""
                    <div class="ranking-item">
                        <div style="flex-grow: 1;">
                            <div class="expression-title">{lei}</div>
                            <div class="info-row">
                                <span>Usos Totais:</span>
                                <strong>{usos}</strong>
                            </div>
                        </div>
                    </div>
            """
        
        html_content += """
                </div>
            </div>
        """
    
    # Seção detalhada de cada expressão
    html_content += """
            <div class="section">
                <h2>📝 Detalhes por Expressão</h2>
    """
    
    for expr, dados in expressoes_ordenadas:
        simplificavel_status = "✅ Simplificável" if dados.get("simplificavel") else "❌ Não Simplificável" if dados.get("simplificavel") is False else "❓ Indeterminado"
        
        html_content += f"""
                <div class="expression-card">
                    <div class="expression-title">{expr}</div>
                    <div class="info-row">
                        <span>Status:</span>
                        <strong>{simplificavel_status}</strong>
                    </div>
                    <div class="info-row">
                        <span>Primeira Tentativa:</span>
                        <span>{dados.get("primeira_tentativa", "N/A")}</span>
                    </div>
                    <div class="info-row">
                        <span>Última Tentativa:</span>
                        <span>{dados.get("ultima_tentativa", "N/A")}</span>
                    </div>
                    
                    <h4>Leis Utilizadas:</h4>
                    <div class="laws-used">
        """
        
        for lei, stats in dados.get("leis_usadas", {}).items():
            sucessos = stats.get("usos_sucesso", 0)
            falhas = stats.get("tentativas_falha", 0)
            
            if sucessos > 0:
                html_content += f'<span class="law-badge success">{lei}: {sucessos} ✓</span>'
            if falhas > 0:
                html_content += f'<span class="law-badge failure">{lei}: {falhas} ✗</span>'
        
        html_content += f"""
                    </div>
                    
                    <div class="info-row">
                        <span>Sessões de Uso:</span>
                        <strong>{len(dados.get("sessoes", []))}</strong>
                    </div>
                </div>
        """
    
    html_content += """
            </div>
        </div>
    </body>
    </html>
    """
    
    # Salvar o arquivo HTML
    with open(output_path, "w", encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Relatório HTML gerado: {output_path}")

# Função para ser chamada periodicamente ou quando necessário
def update_log():
    """Atualiza o relatório HTML com os dados mais recentes"""
    generate_html_log()
    print("Relatório atualizado com sucesso!")
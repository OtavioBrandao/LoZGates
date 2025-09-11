import json
import time
from datetime import datetime

# Função para carregar ou criar o JSON de registro
def load_log(caminho_log="logs.json"):
    try:
        with open(caminho_log, "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "expressions": {},  # CORRIGIDO: usar "expressions" consistentemente
            "estatisticas_gerais": {
                "total_sessoes": 0,
                "expressoes_mais_tentadas": {},
                "leis_mais_usadas": {},
                "tempo_medio_por_expressao": 0
            }
        }
    except json.JSONDecodeError:
        # Se o arquivo existir mas estiver corrompido, cria um novo
        return {
            "expressions": {},
            "estatisticas_gerais": {
                "total_sessoes": 0,
                "expressoes_mais_tentadas": {},
                "leis_mais_usadas": {},
                "tempo_medio_por_expressao": 0
            }
        }

# Função para registrar o uso de uma lei
def register_law(expression, law_name, success=True, tempo_gasto=0, log_path="logs.json"):
    logs = load_log(log_path)

    # CORRIGIDO: usar "expressions" consistentemente
    if expression not in logs["expressions"]:
        logs["expressions"][expression] = {
            "laws_used": {},  # Manter laws_used como estava
            "total_attempts": 0,
            "total_successes": 0,
            "total_time": 0,
            "average_time": 0,
            "simplifiable": None,  # None = ainda não determinado, True = sim, False = não
            "solution_path": [],  # Caminho que levou ao sucesso
            "first_attempt": datetime.now().isoformat(),
            "last_attempt": datetime.now().isoformat(),
            "sessions": []
        }

    # Atualizar dados gerais da expressão
    logs["expressions"][expression]["total_attempts"] += 1
    logs["expressions"][expression]["total_time"] += tempo_gasto
    logs["expressions"][expression]["last_attempt"] = datetime.now().isoformat()
    
    if logs["expressions"][expression]["total_attempts"] > 0:
        logs["expressions"][expression]["average_time"] = (
            logs["expressions"][expression]["total_time"] / 
            logs["expressions"][expression]["total_attempts"]
        )

    # Inicializar lei se não existir
    if law_name not in logs["expressions"][expression]["laws_used"]:
        logs["expressions"][expression]["laws_used"][law_name] = {
            "usos": 0,
            "tentativas_falhas": 0,
            "tempo_gasto": 0
        }

    # Atualizar dados da lei específica
    if success:
        logs["expressions"][expression]["laws_used"][law_name]["usos"] += 1
        logs["expressions"][expression]["total_successes"] += 1
        logs["expressions"][expression]["solution_path"].append(law_name)
        
        # Se teve sucesso, a expressão é simplificável
        if logs["expressions"][expression]["simplifiable"] is None:
            logs["expressions"][expression]["simplifiable"] = True
    else:
        logs["expressions"][expression]["laws_used"][law_name]["tentativas_falhas"] += 1

    logs["expressions"][expression]["laws_used"][law_name]["tempo_gasto"] += tempo_gasto

    # Atualizar estatísticas gerais
    if "estatisticas_gerais" not in logs:
        logs["estatisticas_gerais"] = {
            "total_sessoes": 0,
            "expressoes_mais_tentadas": {},
            "leis_mais_usadas": {},
            "tempo_medio_por_expressao": 0
        }

    # Atualizar contador de leis mais usadas
    if law_name not in logs["estatisticas_gerais"]["leis_mais_usadas"]:
        logs["estatisticas_gerais"]["leis_mais_usadas"][law_name] = 0
    logs["estatisticas_gerais"]["leis_mais_usadas"][law_name] += 1

    # Atualizar contador de expressões mais tentadas
    if expression not in logs["estatisticas_gerais"]["expressoes_mais_tentadas"]:
        logs["estatisticas_gerais"]["expressoes_mais_tentadas"][expression] = 0
    logs["estatisticas_gerais"]["expressoes_mais_tentadas"][expression] += 1

    # Salvar os dados no arquivo com tratamento de erro
    try:
        with open(log_path, "w", encoding='utf-8') as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar logs: {e}")

# Função para gerar relatório HTML (corrigida)
def gerar_relatorio_html(log_path="logs.json", output_path="relatorio_estatisticas.html"):
    """Gera um relatório HTML com as estatísticas dos logs"""
    
    logs = load_log(log_path)
    
    if not logs["expressions"]:  # CORRIGIDO: usar "expressions"
        print("Nenhum dado encontrado para gerar relatório.")
        # Criar um relatório vazio
        with open(output_path, "w", encoding='utf-8') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head><title>Relatório Vazio</title></head>
            <body>
                <h1>Nenhum dado disponível</h1>
                <p>Use o aplicativo para gerar estatísticas!</p>
            </body>
            </html>
            """)
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
            .expression-card {{
                background: #f8f9fa;
                margin: 15px 0;
                padding: 20px;
                border-radius: 8px;
                border-left: 5px solid #3498db;
            }}
            .expression-title {{
                font-family: 'Courier New', monospace;
                font-size: 1.2em;
                font-weight: bold;
                background: #ecf0f1;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Relatório de Estatísticas</h1>
            <p style="text-align: center; color: #7f8c8d;">Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{len(logs["expressions"])}</div>
                    <div>Expressões Testadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(expr["total_attempts"] for expr in logs["expressions"].values())}</div>
                    <div>Tentativas Totais</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(expr.get("total_successes", 0) for expr in logs["expressions"].values())}</div>
                    <div>Sucessos Totais</div>
                </div>
            </div>
            
            <h2>📝 Detalhes das Expressões</h2>
    """
    
    # Adicionar detalhes de cada expressão
    for expression, dados in logs["expressions"].items():
        taxa_sucesso = (dados.get("total_successes", 0) / dados["total_attempts"] * 100) if dados["total_attempts"] > 0 else 0
        
        html_content += f"""
            <div class="expression-card">
                <div class="expression-title">{expression}</div>
                <p><strong>Tentativas:</strong> {dados["total_attempts"]}</p>
                <p><strong>Sucessos:</strong> {dados.get("total_successes", 0)}</p>
                <p><strong>Taxa de Sucesso:</strong> {taxa_sucesso:.1f}%</p>
                <p><strong>Tempo Médio:</strong> {dados.get("average_time", 0):.2f}s</p>
                
                <h4>Leis Utilizadas:</h4>
                <ul>
        """
        
        for lei, stats in dados.get("laws_used", {}).items():
            html_content += f"<li><strong>{lei}:</strong> {stats['usos']} sucessos, {stats['tentativas_falhas']} falhas</li>"
        
        html_content += """
                </ul>
            </div>
        """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Salvar o arquivo HTML
    try:
        with open(output_path, "w", encoding='utf-8') as f:
            f.write(html_content)
        print(f"Relatório HTML gerado com sucesso: {output_path}")
    except Exception as e:
        print(f"Erro ao gerar relatório HTML: {e}")
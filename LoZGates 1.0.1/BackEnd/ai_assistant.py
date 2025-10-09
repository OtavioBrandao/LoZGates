import requests
import json
import threading
import re
from typing import Optional, Callable

class AIAssistant:
    def __init__(self):
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer COLAR CHAVE API"
        }
        
    def get_ai_suggestion(self, expression: str, step_context: str = "", callback: Optional[Callable] = None):
        
        prompt = f"""Analise esta expressão de lógica proposicional e forneça uma sugestão estruturada:

**EXPRESSÃO:** {expression}
**CONTEXTO:** {step_context}

**INSTRUÇÕES:**
1. Identifique qual lei lógica pode ser aplicada
2. Explique o passo de forma clara
3. Mostre o resultado esperado

**LEIS DISPONÍVEIS:**
• **De Morgan:** ¬(A∧B) ≡ ¬A∨¬B | ¬(A∨B) ≡ ¬A∧¬B
• **Distributiva:** A∧(B∨C) ≡ (A∧B)∨(A∧C) | A∨(B∧C) ≡ (A∨B)∧(A∨C)
• **Absorção:** A∧(A∨B) ≡ A | A∨(A∧B) ≡ A
• **Identidade:** A∧1 ≡ A | A∨0 ≡ A
• **Nula:** A∧0 ≡ 0 | A∨1 ≡ 1
• **Inversa:** A∧¬A ≡ 0 | A∨¬A ≡ 1
• **Idempotente:** A∧A ≡ A | A∨A ≡ A

**FORMATO DE RESPOSTA:**
Lei: [Nome da lei]
Aplicação: [Como aplicar]
Resultado: [Expressão resultante]

Responda em português, de forma clara e estruturada."""

        def make_request():
            try:
                payload = {
                    "model": "openai/gpt-oss-120b",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Você é um professor especialista em lógica proposicional. Seja preciso e didático."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 400,
                    "temperature": 0.2
                }
                
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    formatted_response = self._format_response(ai_response)
                    if callback:
                        callback(formatted_response, None)
                else:
                    self._handle_error(response, callback)
                        
            except Exception as e:
                if callback:
                    callback(f"Erro de conexão: {str(e)}", None)
        
        thread = threading.Thread(target=make_request)
        thread.daemon = True
        thread.start()
    
    def ask_question(self, question: str, expression: str, callback: Optional[Callable] = None):
        
        prompt = f"""Responda esta pergunta sobre lógica proposicional de forma estruturada:

**EXPRESSÃO:** {expression}
**PERGUNTA:** {question}

**INSTRUÇÕES:**
1. Responda de forma didática e clara
2. Use exemplos quando necessário
3. Estruture a resposta com tópicos
4. Use símbolos lógicos apropriados (∧, ∨, ¬, →, ↔)

**FORMATO DE RESPOSTA:**
Resposta: [Resposta principal]
Explicação: [Detalhamento]
Exemplo: [Se aplicável]

Responda em português."""

        def make_request():
            try:
                payload = {
                    "model": "openai/gpt-oss-120b",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Você é um professor de lógica proposicional. Seja didático e claro."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.2
                }
                
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    formatted_response = self._format_response(ai_response)
                    if callback:
                        callback(formatted_response, None)
                else:
                    self._handle_error(response, callback)
                        
            except Exception as e:
                if callback:
                    callback(f"Erro de conexão: {str(e)}", None)
        
        thread = threading.Thread(target=make_request)
        thread.daemon = True
        thread.start()
    
    def _format_response(self, response: str) -> str:
        if not response:
            return "Resposta não disponível."
        
        # Remove espaços extras e quebras de linha desnecessárias
        response = re.sub(r'\n\s*\n\s*\n', '\n\n', response.strip())
        
        # Corrige formatação de expressões matemáticas quebradas
        response = self._fix_math_formatting(response)
        
        # Garante que há quebras de linha após pontos finais quando apropriado
        response = re.sub(r'\. ([A-Z])', r'.\n\n\1', response)
        
        # Melhora formatação de listas
        response = re.sub(r'\n- ', '\n• ', response)
        response = re.sub(r'\n\* ', '\n• ', response)
        
        # Substitui símbolos por versões mais legíveis
        symbol_map = {
            '*': '∧',
            '+': '∨', 
            '~': '¬',
            '->': '→',
            '<->': '↔'
        }
        
        for old, new in symbol_map.items():
            response = response.replace(old, new)
        
        return response
    
    def _fix_math_formatting(self, text: str) -> str:
        # Remove quebras de linha dentro de expressões matemáticas
        text = re.sub(r'\(\s*([^)]+?)\s*\)', lambda m: f"({m.group(1).replace(chr(10), '').replace(' ', '')})", text)
        
        # Corrige símbolos quebrados em linhas separadas
        text = re.sub(r'\n\s*([∧∨¬→↔≡])\s*\n', r' \1 ', text)
        text = re.sub(r'([A-Z])\s*\n\s*([∧∨¬→↔≡])\s*\n\s*([A-Z¬])', r'\1 \2 \3', text)
        
        # Remove espaços excessivos em expressões
        text = re.sub(r'([A-Z¬])\s+([∧∨])\s+([A-Z¬])', r'\1\2\3', text)
        
        # Corrige formatação de equivalências
        text = re.sub(r'([A-Z¬()]+)\s*≡\s*([A-Z¬()0-9]+)', r'\1 ≡ \2', text)
        
        return text
    
    def _handle_error(self, response, callback):
        error_msg = "Erro na comunicação com a IA."
        
        if response.status_code == 429:
            error_msg = "Muitas requisições. Tente novamente em alguns segundos."
        elif response.status_code == 401:
            error_msg = "Erro de autenticação. Verifique a chave da API."
        elif response.status_code >= 500:
            error_msg = "Servidor temporariamente indisponível. Tente novamente."
        
        if callback:
            callback(error_msg, response.status_code)
    
    def format_mathematical_text(self, text: str) -> str:
        # Converte símbolos básicos para Unicode
        text = text.replace('~', '¬').replace('*', '∧').replace('+', '∨')
        
        # Corrige a expressão específica mencionada
        text = re.sub(r'\(P~P\)', '(P∧¬P)', text)
        text = re.sub(r'\(~\(P\+Q\)\*\(~Q\+P\)\)', '(¬(P∨Q)∧(¬Q∨P))', text)
        
        # Aplica formatação matemática
        text = self._fix_math_formatting(text)
        
        # Organiza a estrutura da lei
        if 'Lei:' in text and 'Aplicação:' in text:
            text = re.sub(r'Lei:\s*([^\n]+)', r'**Lei:** \1', text)
            text = re.sub(r'Aplicação:\s*', r'\n**Aplicação:**\n', text)
        
        return text
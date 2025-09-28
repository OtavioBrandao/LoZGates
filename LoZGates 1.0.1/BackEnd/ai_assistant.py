import requests
import json
import threading
from typing import Optional, Callable

class AIAssistant:
    def __init__(self):
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer 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"
        }
        
    def get_ai_suggestion(self, expression: str, step_context: str = "", callback: Optional[Callable] = None):
        """Obtém sugestão do Llama 3 via Groq"""
        
        prompt = f"""Você é especialista em lógica proposicional. Analise esta expressão e diga EXATAMENTE qual lei aplicar:

Expressão: {expression}
Contexto: {step_context}

Leis disponíveis:
- De Morgan: ~(A*B) = ~A+~B, ~(A+B) = ~A*~B
- Distributiva: A*(B+C) = A*B+A*C
- Absorção: A*(A+B) = A, A+(A*B) = A
- Identidade: A*1 = A, A+0 = A
- Nula: A*0 = 0, A+1 = 1
- Inversa: A*~A = 0, A+~A = 1
- Idempotente: A*A = A, A+A = A

Seja específico e direto. Responda em português."""

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
                    "max_tokens": 200,
                    "temperature": 0.3
                }
                
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    if callback:
                        callback(ai_response, None)
                else:
                    if callback:
                        error_msg = f"Erro da API: {response.status_code}"
                        try:
                            error_detail = response.json()
                            error_msg += f" - {error_detail}"
                        except:
                            pass
                        callback(error_msg, None)
                        
            except Exception as e:
                if callback:
                    callback(f"Erro de conexão: {str(e)}", None)
        
        thread = threading.Thread(target=make_request)
        thread.daemon = True
        thread.start()
    
    def ask_question(self, question: str, expression: str, callback: Optional[Callable] = None):
        """Faz pergunta específica ao Llama 3"""
        
        prompt = f"""Responda esta pergunta sobre lógica proposicional:

Expressão: {expression}
Pergunta: {question}

Explique de forma clara e educativa. Responda em português."""

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
                    "max_tokens": 300,
                    "temperature": 0.3
                }
                
                response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    if callback:
                        callback(ai_response, None)
                else:
                    if callback:
                        error_msg = f"Erro da API: {response.status_code}"
                        try:
                            error_detail = response.json()
                            error_msg += f" - {error_detail}"
                        except:
                            pass
                        callback(error_msg, None)
                        
            except Exception as e:
                if callback:
                    callback(f"Erro de conexão: {str(e)}", None)
        
        thread = threading.Thread(target=make_request)
        thread.daemon = True
        thread.start()
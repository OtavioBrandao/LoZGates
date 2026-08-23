#Sistema de logging aprimorado para coletar dados detalhados de uso do LoZ Gates.

import json
import os
import time
import hashlib
import platform
import shutil
from datetime import datetime
from typing import Dict, List, Any
import customtkinter as ctk
import logging

from BackEnd import converter
from config import (
    ACTIVITY_LOG_PATH,
    ACTIVITY_SETTINGS_PATH,
    LEGACY_ACTIVITY_LOG_PATH,
    LEGACY_ACTIVITY_SETTINGS_PATH,
    make_window_visible_robust,
)
from FrontEnd.responsive import calculate_window_layout


logger = logging.getLogger(__name__)

class DetailedUserLogger: #Sistema de logging detalhado para coleta de dados granulares de uso.
    
    def __init__(self, app_version="1.0-beta"):
        self.app_version = app_version
        self.log_file = str(ACTIVITY_LOG_PATH)
        self.settings_file = str(ACTIVITY_SETTINGS_PATH)
        ACTIVITY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_files()
        
        #ID anônimo do usuário (baseado no hardware)
        self.user_id = self._generate_anonymous_id()
        
        #Configurações de logging
        self.logging_enabled = True
        self.auto_send_enabled = False
        self.send_frequency_days = 7
        
        #Dados da sessão atual
        self.session_start = time.time()
        self.current_session = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "user_id": self.user_id,
            "app_version": self.app_version,
            "platform": platform.platform(),
            "events": [],
            
            #Contadores detalhados da sessão
            "session_stats": {
                "expressions_entered": 0,
                "expressions_valid": 0,
                "expressions_invalid": 0,
                "equivalence_checks": 0,
                "circuit_generations": 0,
                "interactive_sessions": 0,
                "problems_solved": 0,
                "errors_encountered": 0
            },
            
            #Dados específicos por funcionalidade
            "interactive_simplification": {
                "sessions_started": 0,
                "total_steps": 0,
                "laws_applied": {}, 
                "skips_used": 0,
                "undo_operations": 0,
                "expressions_completed": 0,
                "average_steps_per_session": 0
            },
            
            "interactive_circuit": {
                "sessions_started": 0,
                "components_added": {},  
                "components_deleted": 0,
                "connections_made": 0,
                "test_attempts": 0,
                "successful_circuits": 0,
                "failed_circuits": 0,
                "undo_operations": 0
            },
            
            "equivalence_analysis": {
                "total_checks": 0,
                "equivalent_pairs": 0,
                "non_equivalent_pairs": 0,
                "expression_pairs": []  
            },
            
            "expression_patterns": {
                "variable_counts": {},  
                "operator_usage": {"AND": 0, "OR": 0, "NOT": 0},
                "expression_lengths": {},  
                "common_expressions": {}  
            }
        }
        
        #Carrega configurações existentes
        self._load_settings()
        self._initialize_log_file()

    def _migrate_legacy_files(self):
        """Preserva configuracao e historico das versoes que gravavam na raiz."""
        for source, destination in (
            (LEGACY_ACTIVITY_LOG_PATH, ACTIVITY_LOG_PATH),
            (LEGACY_ACTIVITY_SETTINGS_PATH, ACTIVITY_SETTINGS_PATH),
        ):
            if destination.exists() or not source.exists():
                continue
            try:
                shutil.copy2(source, destination)
            except OSError:
                logger.warning(
                    "Nao foi possivel migrar %s para %s",
                    source,
                    destination,
                    exc_info=True,
                )
    
    def _generate_anonymous_id(self) -> str: #Gera ID anônimo baseado no hardware do usuário.
        try:
            system_info = f"{platform.machine()}{platform.processor()}{platform.platform()}"
            return hashlib.sha256(system_info.encode()).hexdigest()[:16]
        except:
            return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
    
    def _generate_session_id(self) -> str: #Gera ID único para a sessão atual.
        return hashlib.sha256(f"{self.user_id}{time.time()}".encode()).hexdigest()[:12]
    
    def _load_settings(self): #Carrega configurações de logging de forma segura.
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content:
                        print("⚠️ Arquivo de configurações vazio, usando padrões.")
                        return

                    settings = json.loads(content)
                    self.logging_enabled = settings.get('logging_enabled', True)
                    self.auto_send_enabled = settings.get('auto_send_enabled', False)
                    self.send_frequency_days = settings.get('send_frequency_days', 7)
        
        except json.JSONDecodeError:
            print(f"❌ Erro ao ler o arquivo de configurações '{self.settings_file}'. Pode estar corrompido. Usando padrões.")
        except Exception as e:
            print(f"Erro inesperado ao carregar configurações de logging: {e}")
    
    def _save_settings(self): #Salva configurações de logging.
        try:
            settings = {
                'logging_enabled': self.logging_enabled,
                'auto_send_enabled': self.auto_send_enabled,
                'send_frequency_days': self.send_frequency_days,
                'last_prompt': datetime.now().isoformat()
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def _initialize_log_file(self): #Inicializa arquivo de log se não existir ou estiver corrompido.
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                return
        except (json.JSONDecodeError, FileNotFoundError):
             print(f"⚠️ Arquivo '{self.log_file}' não encontrado ou corrompido. Um novo será criado.")
        
        initial_data = {
            "app_info": {
                "name": "LoZ Gates",
                "version": self.app_version,
                "created": datetime.now().isoformat()
            },
            "sessions": []
        }
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao inicializar arquivo de log: {e}")
    
    def _hash_expression(self, expression: str) -> str: #Cria hash da expressão para análise de padrões sem expor conteúdo.
        return hashlib.md5(expression.encode()).hexdigest()[:8]
    
    def log_event(self, event_type: str, event_data: Dict[str, Any] = None): #Registra um evento no log com timestamp detalhado.
        if not self.logging_enabled:
            return
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": event_data or {}
        }
        
        self.current_session["events"].append(event)
    
    def log_expression_entered(self, expression: str, is_valid: bool): #Registra entrada de uma expressão com análise detalhada.
        if not self.logging_enabled:
            return
            
        #Atualiza contadores
        self.current_session["session_stats"]["expressions_entered"] += 1
        if is_valid:
            self.current_session["session_stats"]["expressions_valid"] += 1
        else:
            self.current_session["session_stats"]["expressions_invalid"] += 1
        
        #Análise da expressão
        variable_count = len(set(c for c in expression if c.isalpha()))
        expr_length = len(expression.replace(" ", ""))
        expr_hash = self._hash_expression(expression)
        
        #Atualiza padrões de expressão
        patterns = self.current_session["expression_patterns"]
        patterns["variable_counts"][str(variable_count)] = patterns["variable_counts"].get(str(variable_count), 0) + 1
        patterns["expression_lengths"][str(expr_length)] = patterns["expression_lengths"].get(str(expr_length), 0) + 1
        patterns["common_expressions"][expr_hash] = patterns["common_expressions"].get(expr_hash, 0) + 1
        
        #Conta operadores
        boolean_expr = converter.converter_para_algebra_booleana(expression) if is_valid else expression
    
        patterns["operator_usage"]["AND"] += boolean_expr.count("*")
        patterns["operator_usage"]["OR"] += boolean_expr.count("+") 
        patterns["operator_usage"]["NOT"] += boolean_expr.count("~")
        
        #Log do evento
        self.log_event("expression_entered", {
            "expression_length": expr_length,
            "variable_count": variable_count,
            "has_and": "*" in expression,
            "has_or": "+" in expression,
            "has_not": "~" in expression,
            "is_valid": is_valid,
            "expression_hash": expr_hash
        })
    
    def log_interactive_simplification_start(self, expression: str): #Inicia uma sessão de simplificação interativa.
        if not self.logging_enabled:
            return
            
        self.current_session["interactive_simplification"]["sessions_started"] += 1
        self.current_session["session_stats"]["interactive_sessions"] += 1
        
        self.log_event("interactive_simplification_start", {
            "expression_hash": self._hash_expression(expression),
            "session_number": self.current_session["interactive_simplification"]["sessions_started"]
        })
    
    def log_law_applied(self, law_name: str, success: bool, step_number: int): #Registra aplicação de lei na simplificação interativa.
        if not self.logging_enabled:
            return
            
        interactive_data = self.current_session["interactive_simplification"]
        
        if success:
            interactive_data["total_steps"] += 1
            interactive_data["laws_applied"][law_name] = interactive_data["laws_applied"].get(law_name, 0) + 1
        
        self.log_event("law_application", {
            "law_name": law_name,
            "success": success,
            "step_number": step_number,
            "timestamp_detail": time.time()
        })
    
    def log_simplification_skip(self, step_number: int): #Registra uso do botão 'pular' na simplificação.
        if not self.logging_enabled:
            return
            
        self.current_session["interactive_simplification"]["skips_used"] += 1
        
        self.log_event("simplification_skip", {
            "step_number": step_number,
            "total_skips_session": self.current_session["interactive_simplification"]["skips_used"]
        })
    
    def log_simplification_undo(self): #Registra uso do undo na simplificação.
        if not self.logging_enabled:
            return
            
        self.current_session["interactive_simplification"]["undo_operations"] += 1
        
        self.log_event("simplification_undo", {
            "total_undos_session": self.current_session["interactive_simplification"]["undo_operations"]
        })
    
    def log_simplification_completed(self, total_steps: int, laws_used: List[str]): #Registra conclusão de uma simplificação.
        if not self.logging_enabled:
            return
            
        interactive_data = self.current_session["interactive_simplification"]
        interactive_data["expressions_completed"] += 1
        
        #Calcula média de passos
        if interactive_data["sessions_started"] > 0:
            interactive_data["average_steps_per_session"] = interactive_data["total_steps"] / interactive_data["sessions_started"]
        
        self.log_event("simplification_completed", {
            "steps_taken": total_steps,
            "laws_sequence": laws_used,
            "completion_rate": interactive_data["expressions_completed"] / interactive_data["sessions_started"]
        })
    
    def log_circuit_interaction_start(self): #Inicia uma sessão de circuito interativo.
        if not self.logging_enabled:
            return
            
        self.current_session["interactive_circuit"]["sessions_started"] += 1
        
        self.log_event("interactive_circuit_start", {
            "session_number": self.current_session["interactive_circuit"]["sessions_started"]
        })
    
    def log_component_action(self, action: str, component_type: str = None): #Registra ações com componentes no circuito interativo.
        if not self.logging_enabled:
            return
            
        circuit_data = self.current_session["interactive_circuit"]
        
        if action == "add" and component_type:
            circuit_data["components_added"][component_type] = circuit_data["components_added"].get(component_type, 0) + 1
        elif action == "delete":
            circuit_data["components_deleted"] += 1
        elif action == "connect":
            circuit_data["connections_made"] += 1
        elif action == "undo":
            circuit_data["undo_operations"] += 1
        
        self.log_event("circuit_component_action", {
            "action": action,
            "component_type": component_type,
            "session_totals": {
                "components_added": sum(circuit_data["components_added"].values()),
                "components_deleted": circuit_data["components_deleted"],
                "connections_made": circuit_data["connections_made"]
            }
        })
    
    def log_circuit_test(self, success: bool, attempt_number: int = None): #Registra teste de circuito.
        if not self.logging_enabled:
            return
            
        circuit_data = self.current_session["interactive_circuit"]
        circuit_data["test_attempts"] += 1
        
        if success:
            circuit_data["successful_circuits"] += 1
        else:
            circuit_data["failed_circuits"] += 1
        
        self.log_event("circuit_test", {
            "success": success,
            "attempt_number": attempt_number or circuit_data["test_attempts"],
            "success_rate": circuit_data["successful_circuits"] / circuit_data["test_attempts"] if circuit_data["test_attempts"] > 0 else 0
        })
    
    def log_equivalence_check_with_expressions(self, expression1: str, expression2: str, result: bool): #Registra verificação de equivalência mantendo as expressões completas.
        if not self.logging_enabled:
            return
        
        equiv_data = self.current_session["equivalence_analysis"]
        equiv_data["total_checks"] += 1
        self.current_session["session_stats"]["equivalence_checks"] += 1
        
        if result:
            equiv_data["equivalent_pairs"] += 1
        else:
            equiv_data["non_equivalent_pairs"] += 1
        
        pair_data = {
            "expr1": expression1[:50] + "..." if len(expression1) > 50 else expression1,
            "expr2": expression2[:50] + "..." if len(expression2) > 50 else expression2,
            "expr1_full": expression1,  
            "expr2_full": expression2,  
            "expr1_hash": self._hash_expression(expression1),
            "expr2_hash": self._hash_expression(expression2),
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "check_number": equiv_data["total_checks"]
        }
        equiv_data["expression_pairs"].append(pair_data)
        
        self.log_event("equivalence_check", {
            "result": result,
            "expr1_preview": expression1[:30],  
            "expr2_preview": expression2[:30], 
            "complexity_difference": abs(len(expression1) - len(expression2))
        })
    
    def log_feature_used(self, feature_name: str, duration_seconds: float = None): #Registra uso de uma funcionalidade.
        if not self.logging_enabled:
            return
            
        data = {"feature": feature_name}
        if duration_seconds:
            data["duration"] = round(duration_seconds, 2)
        
        #Atualiza contadores específicos
        if feature_name == "circuit_generation":
            self.current_session["session_stats"]["circuit_generations"] += 1
        
        self.log_event("feature_used", data)
    
    def log_error(self, error_type: str, error_message: str, context: str = None): #Registra erros encontrados pelo usuário.
        if not self.logging_enabled:
            return
            
        self.current_session["session_stats"]["errors_encountered"] += 1
        
        self.log_event("error_occurred", {
            "error_type": error_type,
            "error_message": error_message[:100],
            "context": context,
            "error_sequence": self.current_session["session_stats"]["errors_encountered"]
        })
    
    def log_tab_changed(self, from_tab: str, to_tab: str): #Registra mudança de aba com timing.
        if not self.logging_enabled:
            return
            
        self.log_event("navigation", {
            "from": from_tab,
            "to": to_tab,
            "session_time": time.time() - self.session_start
        })
    
    def end_session(self): #Finaliza a sessão atual.
        if not self.logging_enabled:
            return
        
        #Calcula duração da sessão
        session_duration = time.time() - self.session_start
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["duration_seconds"] = round(session_duration, 2)
        self.current_session["events_count"] = len(self.current_session["events"])
        
        #Calcula estatísticas finais
        self._calculate_final_stats()
        
        #Salva no arquivo
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"app_info": {}, "sessions": []}
            
            data["sessions"].append(self.current_session)
            
            #Limita o número de sessões armazenadas (últimas 100)
            if len(data["sessions"]) > 100:
                data["sessions"] = data["sessions"][-100:]
            
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"📊 Sessão detalhada salva: {session_duration:.1f}s, {len(self.current_session['events'])} eventos")
            
        except Exception as e:
            print(f"Erro ao salvar sessão: {e}")
    
    def _calculate_final_stats(self):#Calcula estatísticas finais da sessão.
        #Estatísticas de navegação
        nav_events = [e for e in self.current_session["events"] if e["type"] == "navigation"]
        self.current_session["session_stats"]["tab_changes"] = len(nav_events)
        
        #Tempo médio por feature
        feature_events = [e for e in self.current_session["events"] if e["type"] == "feature_used"]
        if feature_events:
            total_feature_time = sum(e["data"].get("duration", 0) for e in feature_events)
            self.current_session["session_stats"]["avg_feature_time"] = round(total_feature_time / len(feature_events), 2)
        
        #Taxa de sucesso geral
        total_attempts = (self.current_session["interactive_circuit"]["test_attempts"] + 
                         self.current_session["interactive_simplification"]["sessions_started"])
        total_successes = (self.current_session["interactive_circuit"]["successful_circuits"] + 
                          self.current_session["interactive_simplification"]["expressions_completed"])
        
        if total_attempts > 0:
            self.current_session["session_stats"]["overall_success_rate"] = round(total_successes / total_attempts, 3)
    
    def get_detailed_summary(self) -> Dict[str, Any]: #Retorna resumo detalhado do uso da aplicação.
        try:
            if not os.path.exists(self.log_file):
                return {}
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sessions = data.get("sessions", [])
            if not sessions:
                return {}
            
            #Agregação de dados
            summary = {
                "overview": {
                    "total_sessions": len(sessions),
                    "total_time_minutes": round(sum(s.get("duration_seconds", 0) for s in sessions) / 60, 1),
                    "avg_session_duration": round(sum(s.get("duration_seconds", 0) for s in sessions) / len(sessions) / 60, 1),
                    "total_events": sum(s.get("events_count", 0) for s in sessions)
                },
                
                "interactive_simplification": {
                    "total_sessions": sum(s.get("interactive_simplification", {}).get("sessions_started", 0) for s in sessions),
                    "total_steps": sum(s.get("interactive_simplification", {}).get("total_steps", 0) for s in sessions),
                    "total_skips": sum(s.get("interactive_simplification", {}).get("skips_used", 0) for s in sessions),
                    "total_undos": sum(s.get("interactive_simplification", {}).get("undo_operations", 0) for s in sessions),
                    "completion_rate": 0,
                    "most_used_laws": {}
                },
                
                "interactive_circuit": {
                    "total_sessions": sum(s.get("interactive_circuit", {}).get("sessions_started", 0) for s in sessions),
                    "components_usage": {},
                    "total_deletions": sum(s.get("interactive_circuit", {}).get("components_deleted", 0) for s in sessions),
                    "total_tests": sum(s.get("interactive_circuit", {}).get("test_attempts", 0) for s in sessions),
                    "success_rate": 0,
                    "total_undos": sum(s.get("interactive_circuit", {}).get("undo_operations", 0) for s in sessions)
                },
                
                "equivalence_checks": {
                    "total_checks": sum(s.get("equivalence_analysis", {}).get("total_checks", 0) for s in sessions),
                    "equivalent_found": sum(s.get("equivalence_analysis", {}).get("equivalent_pairs", 0) for s in sessions),
                    "non_equivalent_found": sum(s.get("equivalence_analysis", {}).get("non_equivalent_pairs", 0) for s in sessions),
                    "recent_checks": []
                },
                
                "expression_patterns": {
                    "common_variable_counts": {},
                    "operator_preferences": {"AND": 0, "OR": 0, "NOT": 0},
                    "complexity_distribution": {}
                },
                
                "error_analysis": {
                    "total_errors": sum(s.get("session_stats", {}).get("errors_encountered", 0) for s in sessions),
                    "error_types": {},
                    "sessions_with_errors": 0
                }
            }
            
            #Calcula estatísticas agregadas
            self._aggregate_detailed_stats(sessions, summary)
            
            return summary
            
        except Exception as e:
            print(f"Erro ao gerar resumo detalhado: {e}")
            return {}
    
    def _aggregate_detailed_stats(self, sessions: List[Dict], summary: Dict):
        #Agrega dados de simplificação interativa
        all_laws = {}
        total_completed = 0  #Contador correto
        
        for session in sessions:
            simpl_data = session.get("interactive_simplification", {})
            
            #Pega as leis aplicadas nesta sessão
            laws = simpl_data.get("laws_applied", {})
            for law, count in laws.items():
                all_laws[law] = all_laws.get(law, 0) + count
            
            #CORREÇÃO CRÍTICA: expressions_completed é o contador de conclusões desta sessão
            #Não é um acumulador, então podemos somar diretamente
            total_completed += simpl_data.get("expressions_completed", 0)
        
        summary["interactive_simplification"]["most_used_laws"] = dict(
            sorted(all_laws.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        #CORREÇÃO: Calcula taxa de conclusão corretamente
        total_simpl_sessions = summary["interactive_simplification"]["total_sessions"]
        if total_simpl_sessions > 0:
            summary["interactive_simplification"]["completion_rate"] = round(
                total_completed / total_simpl_sessions, 3
            )
        
        #Adiciona contador de sessões concluídas ao summary
        summary["interactive_simplification"]["expressions_completed"] = total_completed
        
        #Agrega dados de circuito interativo
        all_components = {}
        for session in sessions:
            components = session.get("interactive_circuit", {}).get("components_added", {})
            for comp, count in components.items():
                all_components[comp] = all_components.get(comp, 0) + count
        
        summary["interactive_circuit"]["components_usage"] = dict(
            sorted(all_components.items(), key=lambda x: x[1], reverse=True)
        )
        
        #Taxa de sucesso do circuito
        total_circuit_tests = summary["interactive_circuit"]["total_tests"]
        total_successful = sum(
            s.get("interactive_circuit", {}).get("successful_circuits", 0) 
            for s in sessions
        )
        if total_circuit_tests > 0:
            summary["interactive_circuit"]["success_rate"] = round(
                total_successful / total_circuit_tests, 3
            )
        
        #Coleta verificações de equivalência recentes (últimas 20)
        all_equiv_checks = []
        for session in sessions:
            checks = session.get("equivalence_analysis", {}).get("expression_pairs", [])
            all_equiv_checks.extend(checks)
        
        #Ordena por timestamp e pega as mais recentes
        all_equiv_checks.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        summary["equivalence_checks"]["recent_checks"] = all_equiv_checks[:20]
        
        #Agrega padrões de expressão
        all_var_counts = {}
        all_operators = {"AND": 0, "OR": 0, "NOT": 0}
        
        for session in sessions:
            patterns = session.get("expression_patterns", {})
            
            #Contagem de variáveis
            var_counts = patterns.get("variable_counts", {})
            for count, freq in var_counts.items():
                all_var_counts[count] = all_var_counts.get(count, 0) + freq
            
            #Uso de operadores
            ops = patterns.get("operator_usage", {})
            for op in all_operators:
                all_operators[op] += ops.get(op, 0)
        
        summary["expression_patterns"]["common_variable_counts"] = dict(
            sorted(all_var_counts.items(), key=lambda x: int(x[0]))
        )
        summary["expression_patterns"]["operator_preferences"] = all_operators
        
        #Agrega tentativas falhadas
        all_failed_attempts = {}
        for session in sessions:
            failed = session.get("interactive_simplification", {}).get("failed_attempts", {})
            for law, failures_list in failed.items():
                if law not in all_failed_attempts:
                    all_failed_attempts[law] = 0
                all_failed_attempts[law] += len(failures_list)
        
        summary["interactive_simplification"]["failed_law_attempts"] = dict(
            sorted(all_failed_attempts.items(), key=lambda x: x[1], reverse=True)[:5]
        )

    
    def should_prompt_data_sharing(self) -> bool: #Verifica se deve mostrar prompt para compartilhar dados.
        return True  #Para testes, sempre mostra
        
    def create_formatted_shareable_data(logger) -> Dict[str, Any]:
        try:
            detailed_summary = logger.get_detailed_summary()
            
            return {
                "app_version": logger.app_version,
                "platform": logger.platform.system() if hasattr(logger, 'platform') else 'Unknown',
                "submission_date": datetime.now().isoformat(),
                "formatted_report": ImprovedDataFormatter.format_for_forms(detailed_summary),
                "raw_data": detailed_summary  #Mantém dados brutos para análise automática
            }
        except Exception as e:
            print(f"Erro ao criar dados compartilháveis formatados: {e}")
            return {}

    def log_simplification_step_failed(self, law_name: str, step_number: int, reason: str = "", expression_state: str = ""): #MODIFIED
        if not self.logging_enabled:
            return

        interactive_data = self.current_session["interactive_simplification"]

        if "failed_attempts" not in interactive_data:
            interactive_data["failed_attempts"] = {}

        if law_name not in interactive_data["failed_attempts"]:
            interactive_data["failed_attempts"][law_name] = [] #MODIFIED to store more details

        #Armazena detalhes da falha
        failure_details = {
            "step": step_number,
            "reason": reason,
            "expression": expression_state,
            "timestamp": time.time()
        }
        interactive_data["failed_attempts"][law_name].append(failure_details)

        self.log_event("law_application_failed", {
            "law_name": law_name,
            "step_number": step_number,
            "reason": reason,
            "expression_state": expression_state, #ADDED
            "timestamp_detail": time.time()
        })

class DetailedDataSharingDialog:
    def __init__(self, logger: DetailedUserLogger):
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
        
        #Preview dos dados
        summary = self.logger.get_detailed_summary()
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
        lines.append(f"📅 Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
        lines.append("=" * 60)
        
        return "\n".join(lines)


class ImprovedGoogleFormsSubmitter:    
    def __init__(self, form_url: str, entry_mapping: Dict[str, str]):
        self.form_url = form_url
        self.entry_mapping = entry_mapping
    
    def submit_data(self, data: Dict[str, Any]) -> bool: #Envia os dados formatados para o Google Forms.
        try:
            import requests
            
            #Usa o relatório formatado ao invés do JSON bruto
            formatted_report = data.get("formatted_report", "")
            
            #Prepara os dados para o formulário
            form_data = {
                self.entry_mapping['app_version']: data.get('app_version', ''),
                self.entry_mapping['platform']: data.get('platform', ''),
                self.entry_mapping['submission_date']: data.get('submission_date', ''),
                self.entry_mapping['summary_json']: formatted_report  
            }
            
            #Envia a requisição POST
            response = requests.post(self.form_url, data=form_data, timeout=10)
            
            if response.status_code == 200:
                print("✅ Dados formatados enviados com sucesso!")
                return True
            else:
                print(f"❌ Erro ao enviar dados. Status: {response.status_code}")
                return False
            
        except Exception as e:
            print(f"❌ Erro durante o envio: {e}")
            return False
        

"""
    Sistema de formatação melhorada para envio de dados para Google Forms
    Torna os dados mais legíveis e organizados para análise manual.
"""

class ImprovedDataFormatter:    
    @staticmethod
    def format_for_forms(detailed_summary: Dict[str, Any]) -> str:
        lines = []
        
        #Cabeçalho
        lines.append("=" * 60)
        lines.append("           RELATÓRIO DE USO - LOZ GATES BETA")
        lines.append("=" * 60)
        lines.append("")
        
        #Seção: Resumo Geral
        overview = detailed_summary.get("overview", {})
        lines.append("📊 RESUMO GERAL:")
        lines.append(f"   • Sessões totais: {overview.get('total_sessions', 0)}")
        lines.append(f"   • Tempo total de uso: {overview.get('total_time_minutes', 0):.1f} minutos")
        lines.append(f"   • Duração média por sessão: {overview.get('avg_session_duration', 0):.1f} minutos")
        lines.append(f"   • Total de eventos: {overview.get('total_events', 0)}")
        lines.append("")
        
        #Seção: Simplificação Interativa
        simpl = detailed_summary.get("interactive_simplification", {})
        lines.append("🔍 SIMPLIFICAÇÃO INTERATIVA:")
        
        total_sessions = simpl.get('total_sessions', 0)
        completed = simpl.get('expressions_completed', 0)
        abandoned = total_sessions - completed
        
        lines.append(f"   • Sessões iniciadas: {total_sessions}")
        lines.append(f"   • Sessões concluídas: {completed}")
        lines.append(f"   • Sessões abandonadas: {abandoned}")
        
        #Taxa de conclusão
        completion_rate = simpl.get('completion_rate', 0) * 100
        lines.append(f"   • Taxa de conclusão: {completion_rate:.1f}%")
        
        lines.append(f"   • Passos realizados: {simpl.get('total_steps', 0)}")
        
        #Médias
        avg_steps = 0
        if total_sessions > 0:
            avg_steps = simpl.get('total_steps', 0) / total_sessions
        lines.append(f"   • Média passos/sessão: {avg_steps:.1f}")
        
        avg_steps_completed = 0
        if completed > 0:
            avg_steps_completed = simpl.get('total_steps', 0) / completed
        lines.append(f"   • Média passos/conclusão: {avg_steps_completed:.1f}")
        
        lines.append(f"   • Vezes que pulou: {simpl.get('total_skips', 0)}")
        lines.append(f"   • Operações de desfazer: {simpl.get('total_undos', 0)}")
        
        most_used_laws = simpl.get('most_used_laws', {})
        if most_used_laws:
            lines.append("   • Leis mais aplicadas:")
            for law, count in list(most_used_laws.items())[:5]:
                law_name = law.split('(')[0].strip()
                lines.append(f"     - {law_name}: {count}x")
        
        #Tentativas falhadas
        failed = simpl.get('failed_law_attempts', {})
        if failed:
            lines.append("   • Leis com mais falhas:")
            for law, count in list(failed.items())[:3]:
                law_name = law.split('(')[0].strip()
                lines.append(f"     - {law_name}: {count}x")
        
        lines.append("")
        
        circuit = detailed_summary.get("interactive_circuit", {})
        lines.append("🔧 CIRCUITO INTERATIVO:")
        lines.append(f"   • Sessões iniciadas: {circuit.get('total_sessions', 0)}")
        lines.append(f"   • Componentes deletados: {circuit.get('total_deletions', 0)}")
        lines.append(f"   • Tentativas de teste: {circuit.get('total_tests', 0)}")
        lines.append(f"   • Taxa de sucesso: {circuit.get('success_rate', 0)*100:.1f}%")
        lines.append(f"   • Operações de desfazer: {circuit.get('total_undos', 0)}")
        
        comp_usage = circuit.get('components_usage', {})
        if comp_usage:
            lines.append("   • Componentes mais usados:")
            for comp, count in list(comp_usage.items())[:5]:
                lines.append(f"     - {comp.upper()}: {count}x")
        lines.append("")
        
        equiv = detailed_summary.get("equivalence_checks", {})
        lines.append("🔄 VERIFICAÇÃO DE EQUIVALÊNCIA:")
        lines.append(f"   • Total de verificações: {equiv.get('total_checks', 0)}")
        if equiv.get('total_checks', 0) > 0:
            lines.append(f"   • Pares equivalentes: {equiv.get('equivalent_found', 0)}")
            lines.append(f"   • Pares não equivalentes: {equiv.get('non_equivalent_found', 0)}")
            
            recent_checks = equiv.get('recent_checks', [])[:5]
            if recent_checks:
                lines.append("   • Últimas verificações:")
                for i, check in enumerate(recent_checks, 1):
                    result_symbol = "✓ Equivalente" if check.get('result') else "✗ Diferentes"
                    expr1 = check.get('expr1_full', 'N/A')
                    expr2 = check.get('expr2_full', 'N/A')
                    preview1 = expr1[:40] + '...' if len(expr1) > 40 else expr1
                    preview2 = expr2[:40] + '...' if len(expr2) > 40 else expr2
                    lines.append(f"     {i}. {result_symbol} | '{preview1}' vs '{preview2}'")
        lines.append("")
        
        patterns = detailed_summary.get("expression_patterns", {})
        lines.append("📝 PADRÕES DE EXPRESSÃO:")
        
        var_counts = patterns.get('common_variable_counts', {})
        if var_counts:
            lines.append("   • Variáveis por expressão:")
            for var_count, frequency in sorted(var_counts.items(), key=lambda x: int(x[0])):
                lines.append(f"     - {var_count} variáveis: {frequency} expressões")
        
        operators = patterns.get('operator_preferences', {})
        total_operators = sum(operators.values())
        if total_operators > 0:
            lines.append("   • Operadores mais usados:")
            for op, count in operators.items():
                percentage = (count / total_operators) * 100
                lines.append(f"     - {op}: {count}x ({percentage:.1f}%)")
        lines.append("")
        
        errors = detailed_summary.get("error_analysis", {})
        lines.append("⚠️  ANÁLISE DE ERROS:")
        lines.append(f"   • Total de erros: {errors.get('total_errors', 0)}")
        lines.append(f"   • Sessões com erros: {errors.get('sessions_with_errors', 0)}")
        lines.append("")
        
        lines.append("💡 INSIGHTS AUTOMÁTICOS:")
        insights = ImprovedDataFormatter._generate_insights(detailed_summary)
        for insight in insights:
            lines.append(f"   • {insight}")
        
        if not insights:
            lines.append("   • Poucos dados para gerar insights ainda")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append(f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
        
    @staticmethod
    def _generate_insights(summary: Dict[str, Any]) -> list:
        insights = []
        
        #Insight sobre simplificação
        simpl = summary.get("interactive_simplification", {})
        if simpl.get('total_sessions', 0) > 0:
            completion_rate = simpl.get('completion_rate', 0)
            if completion_rate < 0.5:
                insights.append("Baixa taxa de conclusão na simplificação - usuários podem estar abandonando")
            
            skip_rate = simpl.get('total_skips', 0) / simpl.get('total_sessions', 1)
            if skip_rate > 2:
                insights.append("Muitos pulos por sessão - leis podem estar confusas")
        
        #Insight sobre circuito
        circuit = summary.get("interactive_circuit", {})
        if circuit.get('total_tests', 0) > 0:
            success_rate = circuit.get('success_rate', 0)
            if success_rate < 0.4:
                insights.append("Baixa taxa de sucesso no circuito - interface pode estar confusa")
            elif success_rate > 0.8:
                insights.append("Alta taxa de sucesso no circuito - usuários estão dominando!")
        
        #Insight sobre equivalência
        equiv = summary.get("equivalence_checks", {})
        if equiv.get('total_checks', 0) > 0:
            equiv_rate = equiv.get('equivalent_found', 0) / equiv.get('total_checks', 1)
            if equiv_rate > 0.7:
                insights.append("Usuários testam principalmente expressões equivalentes")
            elif equiv_rate < 0.3:
                insights.append("Usuários exploram mais expressões diferentes")
        
        #Insight sobre operadores
        patterns = summary.get("expression_patterns", {})
        operators = patterns.get('operator_preferences', {})
        if sum(operators.values()) > 0:
            most_used_op = max(operators.items(), key=lambda x: x[1])
            least_used_op = min(operators.items(), key=lambda x: x[1])
            insights.append(f"Operador '{most_used_op[0]}' mais usado, '{least_used_op[0]}' menos usado")
        
        return insights

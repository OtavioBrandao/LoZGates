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
from FrontEnd.utils.responsive import calculate_window_layout


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
        except Exception:
            logger.warning("Nao foi possivel gerar ID anonimo estavel", exc_info=True)
            return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
    
    def _generate_session_id(self) -> str: #Gera ID único para a sessão atual.
        return hashlib.sha256(f"{self.user_id}{time.time()}".encode()).hexdigest()[:12]
    
    def _load_settings(self): #Carrega configurações de logging de forma segura.
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content:
                        logger.warning("Arquivo de configuracoes vazio; usando padroes")
                        return

                    settings = json.loads(content)
                    self.logging_enabled = settings.get('logging_enabled', True)
                    self.auto_send_enabled = settings.get('auto_send_enabled', False)
                    self.send_frequency_days = settings.get('send_frequency_days', 7)
        
        except json.JSONDecodeError:
            logger.warning(
                "Arquivo de configuracoes corrompido em %s; usando padroes",
                self.settings_file,
            )
        except Exception:
            logger.exception("Erro inesperado ao carregar configuracoes de atividade")
    
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
        except Exception:
            logger.exception("Erro ao salvar configuracoes de atividade")
    
    def _initialize_log_file(self): #Inicializa arquivo de log se não existir ou estiver corrompido.
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                return
        except (json.JSONDecodeError, FileNotFoundError):
             logger.warning("Arquivo de atividade ausente ou corrompido em %s", self.log_file)
        
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
        except Exception:
            logger.exception("Erro ao inicializar arquivo de atividade")
    
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
        
        completion_rate = 0.0
        if interactive_data["sessions_started"] > 0:
            completion_rate = interactive_data["expressions_completed"] / interactive_data["sessions_started"]
            
        self.log_event("simplification_completed", {
            "steps_taken": total_steps,
            "laws_sequence": laws_used,
            "completion_rate": completion_rate
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
            
            logger.info(
                "Sessao de atividade salva: %.1fs, %s eventos",
                session_duration,
                len(self.current_session["events"]),
            )
            
        except Exception:
            logger.exception("Erro ao salvar sessao de atividade")
    
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
    
    def _calculate_summary_for_sessions(self, sessions: List[Dict]) -> Dict[str, Any]:
        if not sessions:
            return {}
            
        #Agregação de dados
        summary = {
            "overview": {
                "total_sessions": len(sessions),
                "total_time_minutes": round(sum(s.get("duration_seconds", 0) for s in sessions) / 60, 1),
                "avg_session_duration": round(sum(s.get("duration_seconds", 0) for s in sessions) / max(len(sessions), 1) / 60, 1),
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
        
        # PRESERVAR 100% DOS DADOS: Adiciona as sessões brutas completas (raw data) ao resumo
        summary["sessions"] = sessions
        
        return summary
        
    def get_detailed_summary(self) -> Dict[str, Any]: #Retorna resumo detalhado de TODAS as sessões (histórico).
        try:
            if not os.path.exists(self.log_file):
                return {}
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sessions = data.get("sessions", [])
            return self._calculate_summary_for_sessions(sessions)
            
        except Exception:
            logger.exception("Erro ao gerar resumo detalhado de atividade do histórico")
            return {}

    def get_current_session_summary(self) -> Dict[str, Any]: #Retorna resumo APENAS da sessão atual.
        try:
            #Garante propriedades de fim de sessão se ainda não tiverem sido geradas
            if "duration_seconds" not in self.current_session:
                self.current_session["duration_seconds"] = round(time.time() - self.session_start, 2)
            if "events_count" not in self.current_session:
                self.current_session["events_count"] = len(self.current_session["events"])
                
            return self._calculate_summary_for_sessions([self.current_session])
        except Exception:
            logger.exception("Erro ao gerar resumo da sessão atual")
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
            for op, freq in ops.items():
                all_operators[op] = all_operators.get(op, 0) + freq
        
        summary["expression_patterns"]["common_variable_counts"] = all_var_counts
        summary["expression_patterns"]["operator_preferences"] = all_operators
        
        #Agrega análise de erros
        all_errors = {}
        sessions_with_errors = 0
        
        for session in sessions:
            has_error = False
            for event in session.get("events", []):
                if event.get("type") == "error_occurred":
                    has_error = True
                    err_type = event.get("data", {}).get("error_type", "unknown")
                    all_errors[err_type] = all_errors.get(err_type, 0) + 1
            
            if has_error:
                sessions_with_errors += 1
                
        summary["error_analysis"]["error_types"] = all_errors
        summary["error_analysis"]["sessions_with_errors"] = sessions_with_errors
        
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
        
    @staticmethod
    def create_formatted_shareable_data(logger) -> Dict[str, Any]:
        import platform
        import json
        import os
        from datetime import datetime
        from FrontEnd.services.google_forms_service import ImprovedDataFormatter
        try:
            #Usa APENAS a sessão atual para o relatório e Google Forms
            current_session_summary = logger.get_current_session_summary()
            
            return {
                "app_version": "1.0",
                "platform": platform.system(),
                "submission_date": datetime.now().isoformat(),
                "summary_json": current_session_summary,
                "formatted_report": ImprovedDataFormatter.format_for_forms(current_session_summary)
            }
        except Exception:
            logger.exception("Erro ao criar dados de atividade compartilháveis")
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


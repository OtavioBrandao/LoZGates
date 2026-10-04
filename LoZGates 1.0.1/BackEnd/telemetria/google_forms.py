"""
Envio dos dados de uso ao Google Forms da pesquisa e textos que descrevem
esses dados para o aluno (a prévia do diálogo de consentimento).

Mesmo conteúdo do interface_update (google_forms_service.py e o
_create_data_preview do diálogo de compartilhamento), sem interface.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict

import requests

logger = logging.getLogger(__name__)

# Mesmos valores de LOZGatesApp.on_closing
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd9QNzL1_1MpD0cy_PUA4b59Kpy998015HIsfIT60VC6nOHZA/formResponse"
ENTRY_MAPPING = {
    'app_version': 'entry.695751574',
    'platform': 'entry.2115172041',
    'submission_date': 'entry.1953189469',
    'summary_json': 'entry.415910834'
}


class ImprovedGoogleFormsSubmitter:
    def __init__(self, form_url: str = FORM_URL, entry_mapping: Dict[str, str] = None, sessao=None):
        self.form_url = form_url
        self.entry_mapping = entry_mapping or ENTRY_MAPPING
        self.sessao = sessao or requests

    def submit_data(self, data: Dict[str, Any]) -> bool: #Envia os dados formatados para o Google Forms.
        form_data = {}
        for key, entry_id in self.entry_mapping.items():
            if key in data:
                if isinstance(data[key], (dict, list)):
                    form_data[entry_id] = json.dumps(data[key], ensure_ascii=False)
                else:
                    form_data[entry_id] = data[key]

        logger.info("Enviando dados estruturados para Google Forms: %s campos", len(form_data))

        try:
            response = self.sessao.post(self.form_url, data=form_data, timeout=10)
        except requests.RequestException:
            logger.exception("Erro durante o envio de dados")
            return False

        if response.status_code == 200:
            logger.info("Dados formatados enviados com sucesso")
            return True
        logger.warning("Falha no envio de dados: HTTP %s", response.status_code)
        return False


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


def criar_previa(summary: Dict[str, Any]) -> str:
    """Texto da prévia mostrada no diálogo de consentimento (só a sessão atual)."""
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
    lines.append(f"📅 Relatório gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    lines.append("=" * 60)

    return "\n".join(lines)

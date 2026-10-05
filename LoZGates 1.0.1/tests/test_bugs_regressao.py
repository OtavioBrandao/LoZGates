"""
Regressões de bugs já corrigidos que continuam valendo na versão web.

Os bugs 1 e 2 eram da interface CustomTkinter (que saiu da web-unificado, D5).
O bug 4 (o circuito interativo não registrava as ações) agora é coberto pelo
teste do editor em TypeScript (frontend/src/circuito/editor/modelo.test.ts).
"""
import inspect
import unittest

from BackEnd.telemetria import google_forms
from BackEnd.telemetria.registro_uso import DetailedUserLogger


class TestRegressionBugs(unittest.TestCase):

    def test_bug_3_sem_divisao_por_zero_ao_concluir_simplificacao(self):
        """BUG 3: ZeroDivisionError se nenhuma sessão interativa tivesse começado."""
        logger = DetailedUserLogger("1.0-beta", persistir=False)
        logger.current_session["interactive_simplification"]["sessions_started"] = 0
        logger.current_session["interactive_simplification"]["expressions_completed"] = 1
        try:
            logger.log_simplification_completed(5, ["identidade"])
        except ZeroDivisionError:
            self.fail("ZeroDivisionError ao registrar a conclusão da simplificação")

    def test_bug_5_google_forms_recebe_o_json_bruto(self):
        """BUG 5: o envio usa o campo summary_json e não sobrepõe com formatted_report."""
        self.assertIn("summary_json", google_forms.ENTRY_MAPPING)
        self.assertNotIn("formatted_report", google_forms.ENTRY_MAPPING)
        enviados = []

        class Sessao:
            def post(self, url, data=None, timeout=None, **_):
                enviados.append(data)

                class Resposta:
                    status_code = 200

                return Resposta()

        enviador = google_forms.ImprovedGoogleFormsSubmitter(sessao=Sessao())
        logger = DetailedUserLogger("1.0-beta", persistir=False)
        self.assertTrue(enviador.submit_data(DetailedUserLogger.create_formatted_shareable_data(logger)))
        (campos,) = enviados
        self.assertEqual(set(campos), set(google_forms.ENTRY_MAPPING.values()))

    def test_bug_4_registro_do_editor_esta_no_frontend(self):
        """O registro das ações do circuito é feito pelo editor web (log_component_action)."""
        from pathlib import Path

        raiz = Path(inspect.getfile(google_forms)).resolve().parents[2]
        candidatos = list(raiz.glob("*/src/circuito/editor/modelo.ts"))
        self.assertTrue(candidatos, "editor do circuito não encontrado")
        fonte = candidatos[0].read_text(encoding="utf-8")
        for acao in ("'add'", "'connect'", "'delete'", "'undo'"):
            self.assertIn(acao, fonte)


if __name__ == '__main__':
    unittest.main()

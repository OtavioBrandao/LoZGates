"""O oráculo só vale se for idêntico ao interface_update (fora a troca mecânica dos imports)."""
import hashlib

from tests.paridade import oraculo


def test_arquivos_do_oraculo_batem_com_o_manifesto():
    dados = oraculo.manifesto()
    assert dados["arquivos"], "manifesto vazio"
    for relativo, info in dados["arquivos"].items():
        texto = (oraculo.PASTA / relativo).read_text(encoding="utf-8").replace("\r\n", "\n")
        original = texto.replace(f"{oraculo.PACOTE}.", "")
        assert hashlib.sha256(original.encode("utf-8")).hexdigest() == info["sha256_original"], relativo


def test_oraculo_e_a_logica_antiga_e_nao_a_nova():
    antigo = oraculo.modulo("BackEnd.simplificador_interativo")
    from BackEnd import simplificador_interativo as novo
    assert antigo is not novo
    assert hasattr(antigo, "Node")  # o oráculo ainda tem a classe local que a versão nova removeu
    assert not hasattr(novo, "Node")

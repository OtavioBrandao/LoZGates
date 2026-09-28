"""
Rede no navegador.

O código original usa `requests.post(...)` dentro de `threading.Thread` (assistente
de IA) e `requests.post(...)` direto (envio dos dados de uso para o Google Forms).
No navegador não existem sockets nem threads; quem faz a requisição é o fetch() do
JavaScript, que é assíncrono.

Para reaproveitar o código original SEM alterá-lo, cada chamada roda em duas fases:

  1. CAPTURA   — executamos a função original; quando ela chama requests.post(),
                 guardamos a requisição (url, cabeçalhos, corpo) e interrompemos.
                 O JavaScript então faz o fetch() de verdade.
  2. RESPOSTA  — executamos a mesma função de novo; desta vez requests.post()
                 devolve a resposta que o fetch() recebeu. A partir daí o código
                 original segue normalmente (formatação, tratamento de erro, callback).

A montagem do prompt/corpo é determinística, então as duas execuções são idênticas.
"""

import json as _json
import sys
import types


class RequisicaoCapturada(BaseException):
    """
    Interrompe a função original na fase de captura.

    Herda de BaseException (e não de Exception) de propósito: o código original faz
    `except Exception as e: callback(f"Erro de conexão: {e}")`, e não queremos que
    a captura seja confundida com um erro de rede.
    """

    def __init__(self, pedido):
        super().__init__("requisição capturada")
        self.pedido = pedido


class RespostaWeb:
    """O pedaço de requests.Response que o código original usa."""

    def __init__(self, status_code, texto="", url=""):
        self.status_code = int(status_code)
        self.text = texto or ""
        self.content = self.text.encode("utf-8")
        self.url = url
        self.ok = 200 <= self.status_code < 400

    def json(self):
        return _json.loads(self.text)

    def raise_for_status(self):
        if not self.ok:
            raise ErroHTTP(f"{self.status_code} Error for url: {self.url}")


class ErroRequisicao(IOError):
    pass


class ErroConexao(ErroRequisicao):
    pass


class ErroTimeout(ErroRequisicao):
    pass


class ErroHTTP(ErroRequisicao):
    pass


_estado = {"modo": None, "resposta": None}


def _requisitar(metodo, url, params=None, data=None, json=None, headers=None, timeout=None, **_):
    modo = _estado["modo"]
    if modo == "capturar":
        raise RequisicaoCapturada(
            {
                "metodo": metodo,
                "url": url,
                "params": params,
                "cabecalhos": dict(headers or {}),
                "json": json,
                "form": data if isinstance(data, dict) else None,
                "corpo": data if isinstance(data, str) else None,
                "timeout": timeout,
            }
        )
    if modo == "responder":
        resposta = _estado["resposta"] or {}
        if resposta.get("erro"):
            if resposta.get("timeout"):
                raise ErroTimeout(resposta["erro"])
            raise ErroConexao(resposta["erro"])
        return RespostaWeb(resposta.get("status", 0), resposta.get("texto", ""), url)
    raise ErroConexao("Requisição de rede feita fora do fluxo do navegador.")


def criar_modulo_requests():
    """Módulo `requests` mínimo, com a mesma cara do original para o código do LoZ Gates."""
    modulo = types.ModuleType("requests")
    modulo.__file__ = "<lozweb:requests>"
    modulo.post = lambda url, **kw: _requisitar("POST", url, **kw)
    modulo.get = lambda url, **kw: _requisitar("GET", url, **kw)
    modulo.put = lambda url, **kw: _requisitar("PUT", url, **kw)
    modulo.delete = lambda url, **kw: _requisitar("DELETE", url, **kw)
    modulo.request = lambda metodo, url, **kw: _requisitar(metodo.upper(), url, **kw)
    modulo.Response = RespostaWeb
    excecoes = types.ModuleType("requests.exceptions")
    excecoes.RequestException = ErroRequisicao
    excecoes.ConnectionError = ErroConexao
    excecoes.Timeout = ErroTimeout
    excecoes.HTTPError = ErroHTTP
    modulo.exceptions = excecoes
    modulo.RequestException = ErroRequisicao
    modulo.ConnectionError = ErroConexao
    modulo.Timeout = ErroTimeout
    modulo.HTTPError = ErroHTTP
    return modulo, excecoes


def instalar_requests():
    modulo, excecoes = criar_modulo_requests()
    sys.modules["requests"] = modulo
    sys.modules["requests.exceptions"] = excecoes


def capturar(funcao):
    """Fase 1. Devolve o pedido que a função tentou fazer (ou None se não fez nenhum)."""
    anterior = dict(_estado)
    _estado["modo"] = "capturar"
    try:
        funcao()
        return None
    except RequisicaoCapturada as captura:
        return captura.pedido
    finally:
        _estado.update(anterior)


def responder(funcao, resposta):
    """
    Fase 2. `resposta` = {"status": int, "texto": str} ou {"erro": str, "timeout": bool}.
    """
    anterior = dict(_estado)
    _estado["modo"] = "responder"
    _estado["resposta"] = resposta
    try:
        return funcao()
    finally:
        _estado.update(anterior)


# --------------------------------------------------------------------------
# threading síncrono (só para o módulo do assistente de IA)
# --------------------------------------------------------------------------

class ThreadSincrona:
    """
    O navegador não tem threads. O assistente de IA original faz:
        thread = threading.Thread(target=make_request); thread.daemon = True; thread.start()
    Aqui start() apenas executa o alvo — quem torna a espera assíncrona é o fetch().
    """

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, daemon=None):
        self._alvo = target
        self._args = args
        self._kwargs = kwargs or {}
        self.daemon = daemon
        self.name = name

    def start(self):
        if self._alvo:
            self._alvo(*self._args, **self._kwargs)

    def join(self, timeout=None):
        pass

    def is_alive(self):
        return False


threading_sincrono = types.SimpleNamespace(Thread=ThreadSincrona)

"""
LoZ Gates — inicia o servidor web (API + interface) e abre o navegador.

    python main.py                  # http://127.0.0.1:8000
    python main.py --porta 8080 --sem-navegador
    python main.py --host 0.0.0.0   # para alunos acessarem pela rede

A interface é servida a partir de frontend/dist; gere com `npm run build` dentro
de frontend/ (em desenvolvimento, use `npm run dev` e a API com --reload; ver README).
"""
import argparse
import logging
import threading
import webbrowser

from BackEnd.logging_config import configure_logging
from config import ensure_runtime_directories


def main(argumentos=None):
    parser = argparse.ArgumentParser(description="LoZ Gates no navegador")
    parser.add_argument("--host", default="127.0.0.1", help="endereço do servidor (padrão: 127.0.0.1)")
    parser.add_argument("--porta", type=int, default=8000, help="porta do servidor (padrão: 8000)")
    parser.add_argument("--sem-navegador", action="store_true", help="não abre o navegador automaticamente")
    opcoes = parser.parse_args(argumentos)

    ensure_runtime_directories()
    configure_logging()
    logger = logging.getLogger(__name__)

    import uvicorn
    from BackEnd.api.app import PASTA_DO_FRONTEND, app

    if not PASTA_DO_FRONTEND.is_dir():
        logger.warning(
            "Interface não encontrada em %s: rode `npm install` e `npm run build` na pasta da interface. "
            "Só a API (/api) ficará disponível.",
            PASTA_DO_FRONTEND,
        )

    endereco = "127.0.0.1" if opcoes.host in ("0.0.0.0", "::") else opcoes.host
    url = f"http://{endereco}:{opcoes.porta}/"
    if not opcoes.sem_navegador:
        threading.Timer(1.5, webbrowser.open, args=(url,)).start()

    logger.info("Iniciando o LoZ Gates em %s", url)
    uvicorn.run(app, host=opcoes.host, port=opcoes.porta, log_config=None)


if __name__ == "__main__":
    main()

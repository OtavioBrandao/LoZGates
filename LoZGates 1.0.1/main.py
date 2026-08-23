import logging
import os

from BackEnd.logging_config import configure_logging
from config import ensure_runtime_directories


def main():
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    ensure_runtime_directories()
    configure_logging()
    logger = logging.getLogger(__name__)
    try:
        from FrontEnd.interface import inicializar_interface

        logger.info("Iniciando LozGates")
        inicializar_interface()
    except Exception:
        logger.critical("Falha fatal ao iniciar o LozGates", exc_info=True)
        raise


if __name__ == "__main__":
    main()

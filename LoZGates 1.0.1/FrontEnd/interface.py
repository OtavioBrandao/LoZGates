import logging
from FrontEnd.app.loz_app import LOZGatesApp
from FrontEnd.screens.expression.expression_screen import setup_legacy_screens

logger = logging.getLogger(__name__)

def inicializar_interface():
    """
    Fachada/Entrypoint para inicialização do FrontEnd.
    A verdadeira classe de aplicação agora é LOZGatesApp, localizada em FrontEnd/app/loz_app.py.
    """
    logger.info("Inicializando interface via LOZGatesApp (Nova Arquitetura)")
    app = LOZGatesApp()
    app.setup_screens(setup_legacy_screens)
    app.mainloop()

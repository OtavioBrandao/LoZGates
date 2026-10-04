"""
API web do LoZ Gates (FastAPI).

Camada fina: valida a entrada, chama o core e devolve JSON. Nenhuma regra de
negócio mora aqui. Rotas em /api/...; se existir um build do frontend
(frontend/dist), ele é servido na raiz, então um único processo atende tudo.

Rodar em desenvolvimento:
    uvicorn BackEnd.api.app:app --reload        (na pasta "LoZGates 1.0.1")
"""
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from BackEnd.ai_assistant import AIAssistant
from BackEnd.api import erros
from BackEnd.api.rotas import apoio, circuito, logica
from BackEnd.telemetria.google_forms import ImprovedGoogleFormsSubmitter

VERSAO = "1.0.1"
PASTA_DO_FRONTEND = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def criar_app(
    assistente: Optional[AIAssistant] = None,
    enviador_de_formulario: Optional[ImprovedGoogleFormsSubmitter] = None,
    pasta_do_frontend: Optional[Path] = PASTA_DO_FRONTEND,
) -> FastAPI:
    app = FastAPI(title="LoZ Gates", version=VERSAO, docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.state.assistente = assistente or AIAssistant()
    app.state.enviador_de_formulario = enviador_de_formulario or ImprovedGoogleFormsSubmitter()
    erros.registrar(app)

    origens = [o.strip() for o in os.getenv("LOZGATES_CORS_ORIGINS", "").split(",") if o.strip()]
    if origens:
        app.add_middleware(CORSMiddleware, allow_origins=origens, allow_methods=["GET", "POST"], allow_headers=["*"])

    for rotas in (logica.router, circuito.router, apoio.router):
        app.include_router(rotas, prefix="/api")

    @app.get("/api/saude")
    def saude():
        return {"status": "ok", "versao": VERSAO}

    if pasta_do_frontend is not None and Path(pasta_do_frontend).is_dir():
        app.mount("/", StaticFiles(directory=pasta_do_frontend, html=True), name="frontend")

    return app


app = criar_app()

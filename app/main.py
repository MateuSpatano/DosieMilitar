"""
Aplicação principal FastAPI
"""
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import os
import logging
from pathlib import Path

from app.config import settings
from app.db import create_tables
from app.services.auth_service import AuthService
from app.db import get_db
from app.routers import auth, dashboard, database, account

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Upload CSV",
    description="Sistema web para upload e análise de arquivos CSV",
    version="1.0.0"
)

# Configurar middleware de sessão
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    max_age=86400,  # 24 horas
    same_site="lax",
    https_only=False  # True em produção com HTTPS
)

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Incluir routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(database.router)
app.include_router(account.router)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Adicionar headers de segurança"""
    response = await call_next(request)
    
    # Headers de segurança básicos
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response


@app.on_event("startup")
async def startup_event():
    """Evento de inicialização"""
    try:
        # Criar tabelas do banco
        create_tables()
        logger.info("Tabelas do banco criadas/verificadas")
        
        # Criar diretório de uploads
        uploads_dir = Path(settings.uploads_dir)
        uploads_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Diretório de uploads criado: {uploads_dir}")
        
        # Criar operador se configurado
        db = next(get_db())
        try:
            auth_service = AuthService(db)
            if auth_service.create_operator_from_env():
                logger.info("Operador criado a partir das variáveis de ambiente")
        except Exception as e:
            logger.warning(f"Erro ao criar operador: {e}")
        finally:
            db.close()
        
        logger.info("Aplicação iniciada com sucesso")
        
    except Exception as e:
        logger.error(f"Erro na inicialização: {e}")
        raise


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Página inicial - redireciona para login ou dashboard"""
    # Verificar se usuário está logado
    user = request.session.get("user")
    
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    else:
        return RedirectResponse(url="/login", status_code=302)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Sistema funcionando"}


# Handler para erros 404
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handler para páginas não encontradas"""
    return templates.TemplateResponse("base.html", {
        "request": request,
        "error": "Página não encontrada",
        "title": "404 - Página não encontrada"
    })


# Handler para erros 500
@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Handler para erros internos"""
    logger.error(f"Erro interno: {exc}")
    return templates.TemplateResponse("base.html", {
        "request": request,
        "error": "Erro interno do servidor",
        "title": "500 - Erro interno"
    })

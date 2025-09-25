"""
Router de autenticação
"""
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.auth_service import AuthService
from app.security import generate_csrf_token, verify_csrf_token
from app.schemas import UserCreate, UserLogin
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_current_user(request: Request) -> dict | None:
    """Obter usuário atual da sessão"""
    return request.session.get("user")


def require_auth(request: Request) -> dict:
    """Dependency para rotas que requerem autenticação"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
    return user


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    # Se já estiver logado, redirecionar para dashboard
    if get_current_user(request):
        return RedirectResponse(url="/dashboard", status_code=302)
    
    csrf_token = generate_csrf_token()
    request.session["csrf_token"] = csrf_token
    
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "csrf_token": csrf_token
    })


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Processar login"""
    try:
        # Verificar CSRF
        session_token = request.session.get("csrf_token")
        if not verify_csrf_token(csrf_token, session_token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token CSRF inválido"
            )
        
        # Autenticar usuário
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(email, password)
        
        if not user:
            return templates.TemplateResponse("auth/login.html", {
                "request": request,
                "error": "Email ou senha incorretos",
                "csrf_token": generate_csrf_token()
            })
        
        # Salvar na sessão
        request.session["user"] = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value
        }
        
        # Limpar token CSRF
        request.session.pop("csrf_token", None)
        
        return RedirectResponse(url="/dashboard", status_code=302)
        
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": "Erro interno do servidor",
            "csrf_token": generate_csrf_token()
        })


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Página de registro"""
    # Se já estiver logado, redirecionar para dashboard
    if get_current_user(request):
        return RedirectResponse(url="/dashboard", status_code=302)
    
    csrf_token = generate_csrf_token()
    request.session["csrf_token"] = csrf_token
    
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "csrf_token": csrf_token
    })


@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Processar registro"""
    try:
        # Verificar CSRF
        session_token = request.session.get("csrf_token")
        if not verify_csrf_token(csrf_token, session_token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token CSRF inválido"
            )
        
        # Validar senhas
        if password != confirm_password:
            return templates.TemplateResponse("auth/register.html", {
                "request": request,
                "error": "Senhas não coincidem",
                "csrf_token": generate_csrf_token()
            })
        
        if len(password) < 6:
            return templates.TemplateResponse("auth/register.html", {
                "request": request,
                "error": "Senha deve ter pelo menos 6 caracteres",
                "csrf_token": generate_csrf_token()
            })
        
        # Criar usuário
        auth_service = AuthService(db)
        user = auth_service.create_user(name, email, password)
        
        # Salvar na sessão
        request.session["user"] = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value
        }
        
        # Limpar token CSRF
        request.session.pop("csrf_token", None)
        
        return RedirectResponse(url="/dashboard", status_code=302)
        
    except ValueError as e:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": str(e),
            "csrf_token": generate_csrf_token()
        })
    except Exception as e:
        logger.error(f"Erro no registro: {e}")
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": "Erro interno do servidor",
            "csrf_token": generate_csrf_token()
        })


@router.post("/logout")
async def logout(request: Request):
    """Fazer logout"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

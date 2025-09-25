# app/routers/auth.py

from app.dependencies.auth import get_auth_service
from app.dependencies.security import validate_csrf_token
from app.dependencies.validation import validate_password_length, validate_passwords_match
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
import logging
from sqlalchemy.orm import Session
from app.security import generate_csrf_token
from app.services.auth_service import AuthService


logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/login")
async def login(
    request: Request,
    email: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
    _csrf: Annotated[bool, Depends(validate_csrf_token)],
    auth_service: AuthService = Depends(get_auth_service)
):
    """Processar login com dependências"""
    try:
        user = auth_service.authenticate_user(email, password)
        
        if not user:
            return templates.TemplateResponse("auth/login.html", {
                "request": request,
                "error": "Email ou senha incorretos",
                "csrf_token": generate_csrf_token()
            })
        
        request.session["user"] = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value
        }
        
        request.session.pop("csrf_token", None)
        
        return RedirectResponse(url="/dashboard", status_code=302)
        
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": "Erro interno do servidor",
            "csrf_token": generate_csrf_token()
        })


@router.post("/register")
async def register(
    request: Request,
    name: Annotated[str, Form(...)],
    email: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
    confirm_password: Annotated[str, Form(...)],
    _csrf: Annotated[bool, Depends(validate_csrf_token)],
    _passwords_match: Annotated[bool, Depends(validate_passwords_match)],
    _password_length: Annotated[bool, Depends(validate_password_length)],
    auth_service: AuthService = Depends(get_auth_service)
):
    """Processar registro com dependências"""
    try:
        user = auth_service.create_user(name, email, password)
        
        request.session["user"] = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value
        }
        
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
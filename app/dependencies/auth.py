# app/dependencies/auth.py

from fastapi import Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import Optional, Dict
from app.services.auth_service import AuthService
from app.dependencies.database import get_db
from sqlalchemy.orm import Session

def get_current_user(request: Request) -> Optional[dict]:
    """Obter usuário atual da sessão"""
    return request.session.get("user")

def require_auth(user: dict = Depends(get_current_user)) -> dict:
    """Verifica se o usuário está autenticado"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
    return user

def get_user_object(
    db: Session = Depends(get_db),
    session_user: dict = Depends(require_auth)
):
    """Obtem o usuário completo do banco"""
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(session_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency para fornecer o serviço de autenticação""" 
    return AuthService(db)

def redirect_if_authenticated(user: Optional[dict] = Depends(get_current_user)):
    """Dependência para redirecionar usuários já logados."""
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
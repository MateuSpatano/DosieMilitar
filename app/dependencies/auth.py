# app/dependencies/auth.py
from fastapi import Request, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from typing import Optional, Dict
from app.services.auth_service import AuthService
from app.dependencies.database import get_db
from sqlalchemy.orm import Session

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

async def require_auth(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Valida JWT enviado via Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user_data = auth_service.decode_access_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    return user_data

async def get_user_object(
    user_data: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Retorna usuário completo do banco a partir do token."""
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_data["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

async def redirect_if_authenticated(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Redireciona usuário para dashboard se token válido presente."""
    auth_header = request.headers.get("Authorization")
    if auth_header:
        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() == "bearer" and token:
            user_data = auth_service.decode_access_token(token)
            if user_data:
                return RedirectResponse(url="/dashboard", status_code=302)
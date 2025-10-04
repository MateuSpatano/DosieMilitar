# app/routers/auth.py

from app.dependencies.auth import get_auth_service
from app.dependencies.validation import validate_password_length, validate_passwords_match
from fastapi import APIRouter, Request, Form, Depends, HTTPException, Body
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from typing import Annotated
import logging
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService


logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login")
async def login(
    email: str = Body(..., example="usuario@email.com"),
    password: str = Body(..., example="123456"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Processar login recebendo JSON"""
    try:

        # Validação básica
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email e senha são obrigatórios")
        
        user = auth_service.authenticate_user(email, password)
        
        if not user:
            return JSONResponse({"detail": "Usuário ou senha inválidos"}, status_code=401)
        
        token = auth_service.create_access_token({"user_id": user.id, "user_name": user.name, "user_role": user.role})
        return JSONResponse(
            {"access_token": token, "token_type": "bearer"},
            status_code=200
        )

    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor!")


@router.post("/register")
async def register(
    name: str = Body(..., example="João da Silva"),
    email: str = Body(..., example="usuario@email.com"),
    password: str = Body(..., example="123456"),
    confirm_password: str = Body(..., example="123456"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Processar registro via JSON sem Pydantic model"""
    try:

        # Validação básica
        if not all([name, email, password, confirm_password]):
            raise HTTPException(status_code=400, detail="Todos os campos são obrigatórios")
        
        if password != confirm_password:
            raise HTTPException(status_code=400, detail="As senhas não coincidem")
        
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="A senha deve ter no mínimo 6 caracteres")

        # Criação do usuário
        user = auth_service.create_user(name, email, password)
        return JSONResponse({"msg": "Usuário criado com sucesso"}, status_code=201)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro no registro: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor!")
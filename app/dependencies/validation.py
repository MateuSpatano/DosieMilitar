from fastapi import Form, Request, Depends, HTTPException, status
from app.services.auth_service import AuthService
from app.dependencies.auth import require_auth
from app.dependencies.database import get_db
from sqlalchemy.orm import Session

def validate_passwords_match(
    password: str = Form(...),
    confirm_password: str = Form(...)
) -> bool:
    """Verifica se as senhas coincidem"""
    if password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senhas não coincidem"
        )
    return True

def validate_password_length(password: str = Form(...)) -> bool:
    """Verifica comprimento mínimo da senha"""
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha deve ter pelo menos 6 caracteres"
        )
    return True

def validate_password_change(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    auth_service: AuthService = Depends(get_db),
    current_user: dict = Depends(require_auth),
) -> bool:
    """Valida e processa alteração de senha"""
    if new_password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova senha e confirmação não coincidem"
        )
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova senha deve ter pelo menos 6 caracteres"
        )

    success = auth_service.change_password(
        current_user["id"],
        current_password,
        new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao alterar senha"
        )
    return True

def validate_account_deletion(
    request: Request,
    confirm_email: str = Form(...),
    auth_service: AuthService = Depends(get_db),
    current_user: dict = Depends(require_auth),
) -> bool:
    """Valida e processa exclusão de conta"""
    if current_user["role"] == "operator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operadores não podem excluir a própria conta."
        )

    if confirm_email != current_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email de confirmação não confere"
        )

    success = auth_service.delete_user(current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao excluir conta"
        )

    return True
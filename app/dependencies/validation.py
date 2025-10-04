from fastapi import Form, Request, Depends, HTTPException, status
from app.services.auth_service import AuthService
from app.dependencies.auth import require_auth, get_auth_service
from app.dependencies.database import get_db
from sqlalchemy.orm import Session

def validate_password_change_factory():
    async def validate_password_change(
        request: Request,
        auth_service: AuthService = Depends(get_auth_service),
        current_user: dict = Depends(require_auth),
    ):
        body = await request.json()
        current_password = body.get("current_password")
        new_password = body.get("new_password")
        confirm_password = body.get("confirm_password")

        if not all([current_password, new_password, confirm_password]):
            raise HTTPException(
                status_code=400,
                detail="Todos os campos são obrigatórios."
            )

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
            current_user["user_id"],
            current_password,
            new_password
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao alterar senha"
            )

        return True

    return validate_password_change

def validate_account_deletion(
    auth_service: AuthService = Depends(get_auth_service),
    current_user: dict = Depends(require_auth),
) -> bool:
    """Valida e processa exclusão de conta"""
    if current_user["user_role"] == "operator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operadores não podem excluir a própria conta."
        )

    success = auth_service.delete_user(current_user["user_id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao excluir conta"
        )

    return True
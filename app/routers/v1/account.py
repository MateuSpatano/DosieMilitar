# Seu roteador de gerenciamento de conta
# app/routers/account.py

from app.dependencies.validation import validate_account_deletion, validate_password_change
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/change-password")
async def change_password(
    request: Request,
    _ = Depends(validate_password_change)
):
    """Alterar senha."""
    request.session.pop("csrf_token", None)
    return RedirectResponse(
        url="/account?success=Senha alterada com sucesso",
        status_code=302
    )
    
@router.post("/delete")
async def delete_account(
    request: Request,
    _ = Depends(validate_account_deletion)
):
    """Excluir conta."""
    request.session.clear()
    return RedirectResponse(
        url="/login?success=Conta excluída com sucesso",
        status_code=302
    )
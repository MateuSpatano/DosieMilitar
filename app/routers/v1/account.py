# Seu roteador de gerenciamento de conta
# app/routers/account.py

from app.dependencies.validation import validate_account_deletion, validate_password_change_factory
from fastapi import APIRouter, Request, Depends, status, Body
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/change-password")
async def change_password(
    _: bool = Depends(validate_password_change_factory()),
    current_password: str = Body(...),
    new_password: str = Body(...),
    confirm_password: str = Body(...)
):
    return {"message": "Senha alterada com sucesso"}
    
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
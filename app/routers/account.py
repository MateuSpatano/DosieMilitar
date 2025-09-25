"""
Router de gerenciamento de conta
"""
from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.auth_service import AuthService
from app.security import generate_csrf_token, verify_csrf_token
from app.routers.auth import require_auth
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/account", response_class=HTMLResponse)
async def account_profile(
    request: Request,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Página de perfil da conta"""
    try:
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(current_user["id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return templates.TemplateResponse("account/profile.html", {
            "request": request,
            "user": current_user,
            "user_data": user
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no perfil: {e}")
        return templates.TemplateResponse("account/profile.html", {
            "request": request,
            "user": current_user,
            "error": "Erro ao carregar perfil"
        })


@router.get("/account/change-password", response_class=HTMLResponse)
async def change_password_page(
    request: Request,
    current_user: dict = Depends(require_auth)
):
    """Página de alteração de senha"""
    csrf_token = generate_csrf_token()
    request.session["csrf_token"] = csrf_token
    
    return templates.TemplateResponse("account/change_password.html", {
        "request": request,
        "user": current_user,
        "csrf_token": csrf_token
    })


@router.post("/account/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Alterar senha"""
    try:
        # Verificar CSRF
        session_token = request.session.get("csrf_token")
        if not verify_csrf_token(csrf_token, session_token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token CSRF inválido"
            )
        
        # Validar senhas
        if new_password != confirm_password:
            return templates.TemplateResponse("account/change_password.html", {
                "request": request,
                "user": current_user,
                "error": "Nova senha e confirmação não coincidem",
                "csrf_token": generate_csrf_token()
            })
        
        if len(new_password) < 6:
            return templates.TemplateResponse("account/change_password.html", {
                "request": request,
                "user": current_user,
                "error": "Nova senha deve ter pelo menos 6 caracteres",
                "csrf_token": generate_csrf_token()
            })
        
        # Alterar senha
        auth_service = AuthService(db)
        success = auth_service.change_password(
            current_user["id"],
            current_password,
            new_password
        )
        
        if not success:
            return templates.TemplateResponse("account/change_password.html", {
                "request": request,
                "user": current_user,
                "error": "Erro ao alterar senha",
                "csrf_token": generate_csrf_token()
            })
        
        # Limpar token CSRF
        request.session.pop("csrf_token", None)
        
        return RedirectResponse(
            url="/account?success=Senha alterada com sucesso",
            status_code=302
        )
        
    except ValueError as e:
        return templates.TemplateResponse("account/change_password.html", {
            "request": request,
            "user": current_user,
            "error": str(e),
            "csrf_token": generate_csrf_token()
        })
    except Exception as e:
        logger.error(f"Erro ao alterar senha: {e}")
        return templates.TemplateResponse("account/change_password.html", {
            "request": request,
            "user": current_user,
            "error": "Erro interno do servidor",
            "csrf_token": generate_csrf_token()
        })


@router.get("/account/delete", response_class=HTMLResponse)
async def delete_account_page(
    request: Request,
    current_user: dict = Depends(require_auth)
):
    """Página de confirmação de exclusão da conta"""
    # Operador não pode excluir a própria conta
    if current_user["role"] == "operator":
        return RedirectResponse(
            url="/account?error=Operador não pode excluir a própria conta",
            status_code=302
        )
    
    csrf_token = generate_csrf_token()
    request.session["csrf_token"] = csrf_token
    
    return templates.TemplateResponse("account/delete_confirm.html", {
        "request": request,
        "user": current_user,
        "csrf_token": csrf_token
    })


@router.post("/account/delete")
async def delete_account(
    request: Request,
    confirm_email: str = Form(...),
    csrf_token: str = Form(...),
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Excluir conta"""
    try:
        # Verificar CSRF
        session_token = request.session.get("csrf_token")
        if not verify_csrf_token(csrf_token, session_token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token CSRF inválido"
            )
        
        # Operador não pode excluir a própria conta
        if current_user["role"] == "operator":
            return RedirectResponse(
                url="/account?error=Operador não pode excluir a própria conta",
                status_code=302
            )
        
        # Verificar confirmação do email
        if confirm_email != current_user["email"]:
            return templates.TemplateResponse("account/delete_confirm.html", {
                "request": request,
                "user": current_user,
                "error": "Email de confirmação não confere",
                "csrf_token": generate_csrf_token()
            })
        
        # Excluir usuário
        auth_service = AuthService(db)
        success = auth_service.delete_user(current_user["id"])
        
        if not success:
            return templates.TemplateResponse("account/delete_confirm.html", {
                "request": request,
                "user": current_user,
                "error": "Erro ao excluir conta",
                "csrf_token": generate_csrf_token()
            })
        
        # Limpar sessão e redirecionar
        request.session.clear()
        return RedirectResponse(
            url="/login?success=Conta excluída com sucesso",
            status_code=302
        )
        
    except Exception as e:
        logger.error(f"Erro ao excluir conta: {e}")
        return templates.TemplateResponse("account/delete_confirm.html", {
            "request": request,
            "user": current_user,
            "error": "Erro interno do servidor",
            "csrf_token": generate_csrf_token()
        })

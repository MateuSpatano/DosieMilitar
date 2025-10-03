from app.dependencies.auth import get_user_object, redirect_if_authenticated, require_auth
from app.dependencies.dashboard import get_dashboard_data
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.security import generate_csrf_token


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, _ = Depends(redirect_if_authenticated)):
    csrf_token = generate_csrf_token()
    request.session["csrf_token"] = csrf_token
    error_message = request.query_params.get("errorLogin")
    
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "csrf_token": csrf_token,
        "errorLogin": error_message
    })

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, _ = Depends(redirect_if_authenticated)):
    """Página de registro."""
    csrf_token = generate_csrf_token()
    request.session["csrf_token"] = csrf_token
    
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "csrf_token": csrf_token
    })

@router.get("/account", response_class=HTMLResponse)
async def account_profile(
    request: Request,
    user_object = Depends(get_user_object) # A dependência faz todo o trabalho!
):
    """Página de perfil da conta."""
    return templates.TemplateResponse("account/profile.html", {
        "request": request,
        "user_data": user_object # user_object já é o objeto do usuário
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

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: dict = Depends(require_auth),
    dashboard_data: dict = Depends(get_dashboard_data)
):
    """Página do dashboard."""
    csrf_token = generate_csrf_token()
    request.session["csrf_token"] = csrf_token
    
    return templates.TemplateResponse("dashboard/index.html", {
        "request": request,
        "user": current_user,
        "csrf_token": csrf_token,
        **dashboard_data  # Descompacta o dicionário de dados da dependência
    })
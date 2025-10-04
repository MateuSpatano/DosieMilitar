from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """HTML público, dados protegidos carregados via JS"""
    return templates.TemplateResponse("dashboard/index.html", {"request": request})

@router.get("/account", response_class=HTMLResponse)
async def account_page(request: Request):
    return templates.TemplateResponse("account/profile.html", {"request": request})

@router.get("/account/change-password", response_class=HTMLResponse)
async def account_page(request: Request):
    return templates.TemplateResponse("account/change_password.html", {"request": request})

@router.get("/database", response_class=HTMLResponse)
async def account_page(request: Request):
    return templates.TemplateResponse("database/list.html", {"request": request})
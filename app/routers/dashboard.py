"""
Router do dashboard
"""
from fastapi import APIRouter, Request, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.auth_service import AuthService
from app.services.file_service import FileService
from app.services.csv_service import CSVService
from app.services.stats_service import StatsService
from app.models import Upload
from app.security import generate_csrf_token, verify_csrf_token
from app.routers.auth import require_auth
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Página do dashboard"""
    try:
        # Obter estatísticas
        stats_service = StatsService(db)
        stats = stats_service.get_dashboard_stats()
        
        # Obter estatísticas militares
        military_stats = stats_service.get_military_stats()
        
        # Preparar dados para o gráfico
        chart_data = {
            "labels": list(stats["dtype_distribution"].keys()),
            "data": list(stats["dtype_distribution"].values())
        }
        
        # Gerar token CSRF para upload
        csrf_token = generate_csrf_token()
        request.session["csrf_token"] = csrf_token
        
        return templates.TemplateResponse("dashboard/index.html", {
            "request": request,
            "user": current_user,
            "stats": stats,
            "chart_data": chart_data,
            "military_stats": military_stats,
            "csrf_token": csrf_token
        })
        
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        return templates.TemplateResponse("dashboard/index.html", {
            "request": request,
            "user": current_user,
            "error": "Erro ao carregar dashboard",
            "csrf_token": generate_csrf_token()
        })


@router.post("/upload-csv")
async def upload_csv(
    request: Request,
    file: UploadFile = File(...),
    csrf_token: str = Form(...),
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Upload de arquivo CSV"""
    try:
        # Verificar CSRF
        session_token = request.session.get("csrf_token")
        if not verify_csrf_token(csrf_token, session_token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token CSRF inválido"
            )
        
        # Verificar extensão
        if not file.filename.lower().endswith('.csv'):
            return RedirectResponse(
                url="/dashboard?error=Arquivo deve ser CSV",
                status_code=302
            )
        
        # Ler conteúdo do arquivo
        content = await file.read()
        
        # Salvar arquivo
        file_service = FileService()
        stored_path, size_bytes = file_service.save_upload_file(content, file.filename)
        
        # Processar CSV
        csv_service = CSVService()
        file_path = file_service.get_file_path(stored_path)
        csv_info = csv_service.get_file_info(file_path)
        
        # Salvar no banco
        upload = Upload(
            user_id=current_user["id"],
            original_name=file.filename,
            stored_path=stored_path,
            size_bytes=size_bytes,
            rows_total=csv_info["rows_total"],
            cols_total=csv_info["cols_total"],
            columns_json=json.dumps(csv_info["columns"]),
            dtypes_json=json.dumps(csv_info["dtypes"]),
            sample_rows_json=json.dumps(csv_info["sample_rows"])
        )
        
        db.add(upload)
        db.commit()
        db.refresh(upload)
        
        # Limpar token CSRF
        request.session.pop("csrf_token", None)
        
        return RedirectResponse(
            url="/dashboard?success=Arquivo enviado com sucesso",
            status_code=302
        )
        
    except ValueError as e:
        return RedirectResponse(
            url=f"/dashboard?error={str(e)}",
            status_code=302
        )
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        return RedirectResponse(
            url="/dashboard?error=Erro interno do servidor",
            status_code=302
        )

"""
Router do banco de dados
"""
from app.dependencies.auth import require_auth
from app.dependencies.upload import get_download_file, get_upload_details, get_upload_service, validate_csv_upload
from app.security import verify_csrf_token
from app.services.upload_service import UploadService
from fastapi import APIRouter, Request, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.db import get_db
from app.models import Upload, User
from app.services.file_service import FileService
from app.services.csv_service import CSVService
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/database", response_class=HTMLResponse)
async def database_list(
    request: Request,
    current_user: dict = Depends(require_auth),
    upload_service: UploadService = Depends(get_upload_service),
    q: str = Query(None, description="Buscar por nome do arquivo"),
    from_date: str = Query(None, description="Data inicial (YYYY-MM-DD)"),
    to_date: str = Query(None, description="Data final (YYYY-MM-DD)"),
    user_id: int = Query(None, description="ID do usuário"),
    page: int = Query(1, ge=1, description="Página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
):
    """Lista de uploads com filtros."""
    try:
        data = upload_service.get_filtered_uploads(
            q=q,
            from_date=from_date,
            to_date=to_date,
            user_id=user_id,
            page=page,
            page_size=page_size
        )
        
        users = upload_service.get_all_users()

        return templates.TemplateResponse("database/list.html", {
            "request": request,
            "user": current_user,
            "uploads": data["uploads"],
            "users": users,
            "filters": {
                "q": q,
                "from_date": from_date,
                "to_date": to_date,
                "user_id": user_id
            },
            "pagination": {
                "page": data["page"],
                "page_size": data["page_size"],
                "total": data["total"],
                "total_pages": data["total_pages"],
                "has_prev": data["page"] > 1,
                "has_next": data["page"] < data["total_pages"]
            }
        })
    except Exception as e:
        logger.error(f"Erro ao listar uploads: {e}")
        return templates.TemplateResponse("database/list.html", {
            "request": request,
            "user": current_user,
            "error": "Erro ao carregar lista de uploads",
            "uploads": [],
            "users": []
        })


@router.get("/database/{upload_id}", response_class=HTMLResponse)
async def database_detail(
    request: Request,
    current_user: dict = Depends(require_auth),
    data: dict = Depends(get_upload_details) # A dependência faz todo o trabalho!
):
    """Detalhes do upload."""
    return templates.TemplateResponse("database/detail.html", {
        "request": request,
        "user": current_user,
        "upload": data["upload"],
        "columns": data["columns"],
        "dtypes": data["dtypes"],
        "sample_rows": data["sample_rows"]
    })


@router.get("/database/{upload_id}/download")
async def download_upload(
    upload_id: int,
    current_user: dict = Depends(require_auth),
    file_data: dict = Depends(get_download_file) # A dependência faz todo o trabalho!
):
    """Download do arquivo original."""
    return FileResponse(
        path=file_data["path"],
        filename=file_data["filename"],
        media_type='text/csv'
    )

@router.post("/upload-csv")
async def upload_csv(
    request: Request,
    file: UploadFile = Depends(validate_csv_upload),
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Upload de arquivo CSV."""
    try:
        upload_service = UploadService(db)
        upload = upload_service.process_and_save_upload(current_user["id"], file)
        
        request.session.pop("csrf_token", None)
        
        return RedirectResponse(
            url="/dashboard?success=Arquivo enviado com sucesso",
            status_code=302
        )
        
    except HTTPException as e:
        # Erro de CSRF ou validação do arquivo
        return RedirectResponse(
            url=f"/dashboard?error={e.detail}",
            status_code=302
        )
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        return RedirectResponse(
            url="/dashboard?error=Erro interno do servidor",
            status_code=302
        )
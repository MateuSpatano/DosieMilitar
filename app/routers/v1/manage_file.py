"""
Router do banco de dados
"""
from app.dependencies.auth import require_auth
from app.dependencies.upload import get_download_file, get_upload_details, get_upload_service, validate_csv_upload
from app.services.upload_service import UploadService
from fastapi import APIRouter, Request, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
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


@router.get("/database")
async def database_list(
    current_user: dict = Depends(require_auth),
    upload_service: UploadService = Depends(get_upload_service),
    q: str = Query(None, description="Buscar por nome do arquivo"),
    from_date: str = Query(None, description="Data inicial (YYYY-MM-DD)"),
    to_date: str = Query(None, description="Data final (YYYY-MM-DD)"),
    user_id: str = Query(None, description="ID do usuário"),
    page: int = Query(1, ge=1, description="Página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
):
    """
    Retorna a lista de uploads em formato JSON.
    """
    try:
        # Se o usuário não for operador ou admin, só pode ver seus próprios uploads
        if current_user["user_role"] not in ("admin", "operator"):
            user_id = current_user["user_id"]

        data = upload_service.get_filtered_uploads(
            q=q,
            from_date=from_date,
            to_date=to_date,
            user_id=user_id,
            page=page,
            page_size=page_size
        )

        return {
            "uploads": data["uploads"],  # certifique-se que isso seja serializável
            "pagination": {
                "page": data["page"],
                "page_size": data["page_size"],
                "total": data["total"],
                "total_pages": data["total_pages"],
                "has_prev": data["page"] > 1,
                "has_next": data["page"] < data["total_pages"]
            },
            "user": {
                "id": current_user["user_id"],
                "name": current_user["user_name"],
                "role": current_user["user_role"]
            }
        }

    except Exception as e:
        logger.error(f"Erro ao listar uploads: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro ao carregar lista de uploads"}
        )


@router.get("/database/{upload_id}")
async def api_database_detail(
    upload_id: int,
    current_user: dict = Depends(require_auth),
    data: dict = Depends(get_upload_details)
):
    """Retorna os detalhes do upload como JSON."""
    upload = data["upload"]

    return {
        "upload": {
            "id": upload.id,
            "original_name": upload.original_name,
            "uploaded_at": upload.uploaded_at.isoformat(),
            "size_bytes": upload.size_bytes,
            "rows_total": upload.rows_total,
            "cols_total": upload.cols_total,
            "user": {
                "id": upload.user.id,
                "name": upload.user.name,
                "role": upload.user.role
            }
        },
        "columns": data["columns"],
        "dtypes": data["dtypes"],
        "sample_rows": data["sample_rows"]
    }


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

@router.post("/upload-csv", response_class=JSONResponse)
async def upload_csv(
    file: UploadFile = Depends(validate_csv_upload),
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Upload de arquivo CSV via JWT + Fetch (JSON)."""
    try:
        upload_service = UploadService(db)
        upload = upload_service.process_and_save_upload(current_user["user_id"], file)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Arquivo enviado com sucesso!", "upload_id": upload.id}
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"message": e.detail}
        )
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Erro interno do servidor"}
        )
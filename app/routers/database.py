"""
Router do banco de dados
"""
from fastapi import APIRouter, Request, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.db import get_db
from app.models import Upload, User
from app.services.file_service import FileService
from app.services.csv_service import CSVService
from app.routers.auth import require_auth
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
    db: Session = Depends(get_db),
    q: str = Query(None, description="Buscar por nome do arquivo"),
    from_date: str = Query(None, description="Data inicial (YYYY-MM-DD)"),
    to_date: str = Query(None, description="Data final (YYYY-MM-DD)"),
    user_id: int = Query(None, description="ID do usuário"),
    page: int = Query(1, ge=1, description="Página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
):
    """Lista de uploads com filtros"""
    try:
        # Construir query
        query = db.query(Upload).join(User)
        
        # Aplicar filtros
        if q:
            query = query.filter(Upload.original_name.ilike(f"%{q}%"))
        
        if from_date:
            try:
                from_dt = datetime.strptime(from_date, "%Y-%m-%d")
                query = query.filter(Upload.uploaded_at >= from_dt)
            except ValueError:
                pass
        
        if to_date:
            try:
                to_dt = datetime.strptime(to_date, "%Y-%m-%d")
                # Adicionar 23:59:59 para incluir o dia inteiro
                to_dt = to_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(Upload.uploaded_at <= to_dt)
            except ValueError:
                pass
        
        if user_id:
            query = query.filter(Upload.user_id == user_id)
        
        # Ordenar por data de upload (mais recente primeiro)
        query = query.order_by(desc(Upload.uploaded_at))
        
        # Paginação
        total = query.count()
        offset = (page - 1) * page_size
        uploads = query.offset(offset).limit(page_size).all()
        
        # Calcular informações de paginação
        total_pages = (total + page_size - 1) // page_size
        has_prev = page > 1
        has_next = page < total_pages
        
        # Obter lista de usuários para filtro
        users = db.query(User).all()
        
        return templates.TemplateResponse("database/list.html", {
            "request": request,
            "user": current_user,
            "uploads": uploads,
            "users": users,
            "filters": {
                "q": q,
                "from_date": from_date,
                "to_date": to_date,
                "user_id": user_id
            },
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_prev": has_prev,
                "has_next": has_next
            }
        })
        
    except Exception as e:
        logger.error(f"Erro na lista de uploads: {e}")
        return templates.TemplateResponse("database/list.html", {
            "request": request,
            "user": current_user,
            "error": "Erro ao carregar lista de uploads",
            "uploads": [],
            "users": [],
            "filters": {},
            "pagination": {}
        })


@router.get("/database/{upload_id}", response_class=HTMLResponse)
async def database_detail(
    upload_id: int,
    request: Request,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Detalhes do upload"""
    try:
        # Buscar upload
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        
        if not upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload não encontrado"
            )
        
        # Parsear JSONs
        columns = []
        dtypes = {}
        sample_rows = []
        
        if upload.columns_json:
            try:
                columns = json.loads(upload.columns_json)
            except (json.JSONDecodeError, TypeError):
                pass
        
        if upload.dtypes_json:
            try:
                dtypes = json.loads(upload.dtypes_json)
            except (json.JSONDecodeError, TypeError):
                pass
        
        if upload.sample_rows_json:
            try:
                sample_rows = json.loads(upload.sample_rows_json)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return templates.TemplateResponse("database/detail.html", {
            "request": request,
            "user": current_user,
            "upload": upload,
            "columns": columns,
            "dtypes": dtypes,
            "sample_rows": sample_rows
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no detalhe do upload: {e}")
        return templates.TemplateResponse("database/detail.html", {
            "request": request,
            "user": current_user,
            "error": "Erro ao carregar detalhes do upload"
        })


@router.get("/database/{upload_id}/download")
async def download_upload(
    upload_id: int,
    current_user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Download do arquivo original"""
    try:
        # Buscar upload
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        
        if not upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload não encontrado"
            )
        
        # Verificar se arquivo existe
        file_service = FileService()
        file_path = file_service.get_file_path(upload.stored_path)
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arquivo não encontrado no servidor"
            )
        
        # Retornar arquivo
        return FileResponse(
            path=str(file_path),
            filename=upload.original_name,
            media_type='text/csv'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no download: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

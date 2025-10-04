from http.client import HTTPException
from typing import Annotated
from app.db import get_db 
from app.models import Upload
from app.services.file_service import FileService
from fastapi import Depends
from fastapi import APIRouter, Request, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
import json
from app.services.upload_service import UploadService

def get_upload_service(db: Session = Depends(get_db)) -> UploadService:
    return UploadService(db)

def get_upload_details(upload_id: int, db: Session = Depends(get_db)):
    """Dependência para obter os detalhes de um upload."""
    upload_service = UploadService(db)
    upload = upload_service.get_upload_by_id(upload_id)

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

    return {
        "upload": upload,
        "columns": columns,
        "dtypes": dtypes,
        "sample_rows": sample_rows
    }

def get_download_file(upload_id: int, db: Session = Depends(get_db)):
    """Dependência para obter o arquivo e suas informações para download."""
    upload = db.query(Upload).filter(Upload.id == upload_id).first()
    
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload não encontrado"
        )
    
    file_service = FileService()
    file_path = file_service.get_file_path(upload.stored_path)
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado no servidor"
        )
    
    return {
        "path": str(file_path),
        "filename": upload.original_name
    }

def validate_csv_upload(
    request: Request, 
    file: UploadFile = File(...)
):
    """Dependência para validar o CSRF e a extensão do arquivo CSV."""
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo deve ser um CSV."
        )
    return file
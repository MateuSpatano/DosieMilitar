# app/services/upload_service.py

from datetime import datetime
from app.services.csv_service import CSVService
from app.services.file_service import FileService
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.models import Upload, User
import json
from fastapi import UploadFile

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class UploadService:
    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService()
        self.csv_service = CSVService()

    def get_filtered_uploads(self, q: str = None, from_date: str = None, to_date: str = None, user_id: str = None, page: int = 1, page_size: int = 10):
        query = self.db.query(Upload).options(joinedload(Upload.user)).join(User)

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
                to_dt = to_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(Upload.uploaded_at <= to_dt)
            except ValueError:
                pass

        if user_id:
            query = query.filter(Upload.user_id == user_id)

        total = query.count()
        query = query.order_by(desc(Upload.uploaded_at))
        offset = (page - 1) * page_size
        uploads = query.offset(offset).limit(page_size).all()
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "uploads": uploads,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    
    def process_and_save_upload(self, user_id: int, file: UploadFile):
        # Salva o arquivo fisicamente
        content = file.file.read()
        stored_path, size_bytes = self.file_service.save_upload_file(content, file.filename)
        
        # Processa o CSV para obter informações
        file_path = self.file_service.get_file_path(stored_path)
        csv_info = self.csv_service.get_file_info(file_path)
        
        # Salva as informações do upload no banco de dados
        upload = Upload(
            user_id=user_id,
            original_name=file.filename,
            stored_path=stored_path,
            size_bytes=size_bytes,
            rows_total=csv_info["rows_total"],
            cols_total=csv_info["cols_total"],
            columns_json=json.dumps(csv_info["columns"]),
            dtypes_json=json.dumps(csv_info["dtypes"]),
            sample_rows_json=json.dumps(csv_info["sample_rows"])
        )
        
        self.db.add(upload)
        self.db.commit()
        self.db.refresh(upload)
        
        return upload

    def get_upload_by_id(self, upload_id: int) -> Upload | None:
        return self.db.query(Upload).filter(Upload.id == upload_id).first()
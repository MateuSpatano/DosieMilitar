from fastapi import APIRouter, Depends
from app.models import User, Upload
from sqlalchemy.orm import Session
from app.db import get_db
from app.dependencies.auth import get_user_object

router = APIRouter()

@router.get("/user-profile")
def get_user_profile(current_user: User = Depends(get_user_object),  db: Session = Depends(get_db)):
    uploads = db.query(Upload).filter(Upload.user_id == current_user.id).all()

    total_uploads = len(uploads)
    total_lines = sum(upload.total_lines or 0 for upload in uploads)
    total_size = sum(upload.file_size or 0 for upload in uploads)

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at.strftime('%Y-%m-%d'),
        "stats": {
            "uploads": total_uploads,
            "lines": total_lines,
            "space_used_mb": round(total_size / (1024 * 1024), 2)
        }
    }

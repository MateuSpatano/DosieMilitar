from app.services.auth_service import AuthService
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models import User, Upload
from sqlalchemy.orm import Session
from app.db import get_db
from app.dependencies.auth import get_user_object, require_auth, get_auth_service

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

@router.get("/users")
async def list_users(
    current_user: dict = Depends(require_auth),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Retorna lista de usuários como dicionários (sem BaseModel).
    """
    try:
        users = auth_service.get_all_users()  # Deve retornar lista de objetos ORM
        result = [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
            for user in users
        ]
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Erro ao carregar usuários: {str(e)}"}
        )
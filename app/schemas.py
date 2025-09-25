"""
Schemas Pydantic para validação de dados
"""
from pydantic import BaseModel
from pydantic import EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import UserRole


# Schemas de usuário
class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True


# Schemas de upload
class UploadResponse(BaseModel):
    id: int
    original_name: str
    size_bytes: int
    uploaded_at: datetime
    rows_total: Optional[int]
    cols_total: Optional[int]
    columns_json: Optional[str]
    dtypes_json: Optional[str]
    sample_rows_json: Optional[str]
    user: UserResponse
    
    class Config:
        from_attributes = True


class UploadDetail(UploadResponse):
    stored_path: str


# Schemas de mudança de senha
class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


# Schemas de filtros
class UploadFilters(BaseModel):
    q: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    user_id: Optional[int] = None
    page: int = 1
    page_size: int = 10


# Schemas de estatísticas
class DashboardStats(BaseModel):
    total_uploads: int
    last_upload: Optional[UploadResponse]
    total_rows: int
    dtype_distribution: Dict[str, int]


# Schemas de CSRF
class CSRFResponse(BaseModel):
    csrf_token: str

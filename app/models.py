"""
Modelos SQLAlchemy
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base
import enum


class UserRole(str, enum.Enum):
    """Roles de usuário"""
    OPERATOR = "operator"
    USER = "user"


class User(Base):
    """Modelo de usuário"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamento com uploads
    uploads = relationship("Upload", back_populates="user")


class Upload(Base):
    """Modelo de upload de arquivo"""
    __tablename__ = "uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_name = Column(String(255), nullable=False)
    stored_path = Column(String(500), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Metadados do CSV
    rows_total = Column(Integer, nullable=True)
    cols_total = Column(Integer, nullable=True)
    columns_json = Column(Text, nullable=True)  # JSON string
    dtypes_json = Column(Text, nullable=True)   # JSON string
    sample_rows_json = Column(Text, nullable=True)  # JSON string
    
    # Relacionamento com usuário
    user = relationship("User", back_populates="uploads")

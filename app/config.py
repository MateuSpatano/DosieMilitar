"""
Configurações da aplicação
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Segurança
    secret_key: str = "change_me"
    
    # Banco de dados
    database_url: str = "sqlite:///./app.db"
    
    # Operador padrão
    operator_email: Optional[str] = None
    operator_password: Optional[str] = None
    
    # Upload
    max_upload_mb: int = 20
    
    # Diretório de uploads
    uploads_dir: str = "./uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instância global das configurações
settings = Settings()

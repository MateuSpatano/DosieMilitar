"""
Utilitários de segurança
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from app.config import settings

# Contexto para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Serializer para tokens
serializer = URLSafeTimedSerializer(settings.secret_key)


def hash_password(password: str) -> str:
    """Hash de senha usando bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar senha"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_csrf_token() -> str:
    """Gerar token CSRF"""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, session_token: str) -> bool:
    """Verificar token CSRF"""
    return secrets.compare_digest(token, session_token)


def format_bytes(bytes_value: int) -> str:
    """Formatar bytes em formato legível"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"


def is_safe_filename(filename: str) -> bool:
    """Verificar se o nome do arquivo é seguro"""
    import os
    # Verificar se contém apenas caracteres seguros
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_")
    return all(c in safe_chars for c in filename) and not os.path.basename(filename).startswith('.')

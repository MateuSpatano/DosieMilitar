"""
Serviço de arquivos
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Tuple
from app.config import settings
from app.security import is_safe_filename
import logging

logger = logging.getLogger(__name__)


class FileService:
    """Serviço de manipulação de arquivos"""
    
    def __init__(self):
        self.uploads_dir = Path(settings.uploads_dir)
        self.max_size_bytes = settings.max_upload_mb * 1024 * 1024
    
    def ensure_uploads_dir(self):
        """Garantir que o diretório de uploads existe"""
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
    
    def get_upload_path(self, original_filename: str) -> Tuple[str, int]:
        """
        Gerar caminho para arquivo de upload
        
        Returns:
            Tuple[str, int]: (caminho_relativo, tamanho_em_bytes)
        """
        # Validar nome do arquivo
        if not is_safe_filename(original_filename):
            raise ValueError("Nome de arquivo inválido")
        
        # Verificar extensão
        if not original_filename.lower().endswith('.csv'):
            raise ValueError("Apenas arquivos CSV são permitidos")
        
        # Criar estrutura de pastas por data
        now = datetime.now()
        year_month_dir = self.uploads_dir / str(now.year) / f"{now.month:02d}"
        year_month_dir.mkdir(parents=True, exist_ok=True)
        
        # Gerar nome único
        file_uuid = str(uuid.uuid4())
        name, ext = os.path.splitext(original_filename)
        unique_filename = f"{file_uuid}_{name}{ext}"
        
        # Caminho completo
        full_path = year_month_dir / unique_filename
        
        return str(full_path.relative_to(self.uploads_dir)), 0
    
    def save_upload_file(self, file_content: bytes, original_filename: str) -> Tuple[str, int]:
        """
        Salvar arquivo de upload
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            original_filename: Nome original do arquivo
            
        Returns:
            Tuple[str, int]: (caminho_relativo, tamanho_em_bytes)
        """
        # Verificar tamanho
        if len(file_content) > self.max_size_bytes:
            raise ValueError(f"Arquivo muito grande. Máximo: {settings.max_upload_mb}MB")
        
        # Garantir diretório
        self.ensure_uploads_dir()
        
        # Gerar caminho
        relative_path, _ = self.get_upload_path(original_filename)
        full_path = self.uploads_dir / relative_path
        
        # Garantir que o diretório pai existe
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Salvar arquivo
        with open(full_path, 'wb') as f:
            f.write(file_content)
        
        return relative_path, len(file_content)
    
    def get_file_path(self, relative_path: str) -> Path:
        """Obter caminho absoluto do arquivo"""
        return self.uploads_dir / relative_path
    
    def file_exists(self, relative_path: str) -> bool:
        """Verificar se arquivo existe"""
        return self.get_file_path(relative_path).exists()
    
    def delete_file(self, relative_path: str) -> bool:
        """Deletar arquivo"""
        try:
            file_path = self.get_file_path(relative_path)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo {relative_path}: {e}")
            return False

"""
Serviço de estatísticas
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models import Upload, User
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class StatsService:
    """Serviço de estatísticas e agregações"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obter estatísticas para o dashboard"""
        try:
            # Total de uploads
            total_uploads = self.db.query(Upload).count()
            
            # Último upload
            last_upload = self.db.query(Upload).order_by(desc(Upload.uploaded_at)).first()
            
            # Total de linhas (soma de todos os uploads)
            total_rows = self.db.query(func.sum(Upload.rows_total)).scalar() or 0
            
            # Distribuição por tipo de dados
            dtype_distribution = self._get_dtype_distribution()
            
            return {
                'total_uploads': total_uploads,
                'last_upload': last_upload,
                'total_rows': total_rows,
                'dtype_distribution': dtype_distribution
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                'total_uploads': 0,
                'last_upload': None,
                'total_rows': 0,
                'dtype_distribution': {}
            }
    
    def _get_dtype_distribution(self) -> Dict[str, int]:
        """Obter distribuição de tipos de dados"""
        try:
            # Buscar todos os dtypes_json
            uploads = self.db.query(Upload).filter(Upload.dtypes_json.isnot(None)).all()
            
            dtype_counts = {}
            
            for upload in uploads:
                try:
                    dtypes = json.loads(upload.dtypes_json)
                    for col, dtype in dtypes.items():
                        dtype_counts[dtype] = dtype_counts.get(dtype, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    continue
            
            return dtype_counts
            
        except Exception as e:
            logger.error(f"Erro ao obter distribuição de tipos: {e}")
            return {}
    
    def get_upload_stats_by_user(self, user_id: int) -> Dict[str, Any]:
        """Obter estatísticas de uploads por usuário"""
        try:
            # Total de uploads do usuário
            total_uploads = self.db.query(Upload).filter(Upload.user_id == user_id).count()
            
            # Total de linhas do usuário
            total_rows = self.db.query(func.sum(Upload.rows_total)).filter(
                Upload.user_id == user_id
            ).scalar() or 0
            
            # Tamanho total dos arquivos
            total_size = self.db.query(func.sum(Upload.size_bytes)).filter(
                Upload.user_id == user_id
            ).scalar() or 0
            
            return {
                'total_uploads': total_uploads,
                'total_rows': total_rows,
                'total_size_bytes': total_size
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do usuário: {e}")
            return {
                'total_uploads': 0,
                'total_rows': 0,
                'total_size_bytes': 0
            }
    
    def get_recent_uploads(self, limit: int = 10) -> list:
        """Obter uploads recentes"""
        try:
            return self.db.query(Upload).order_by(desc(Upload.uploaded_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"Erro ao obter uploads recentes: {e}")
            return []
    
    def get_uploads_by_date_range(self, start_date, end_date):
        """Obter uploads por período"""
        try:
            query = self.db.query(Upload)
            
            if start_date:
                query = query.filter(Upload.uploaded_at >= start_date)
            
            if end_date:
                query = query.filter(Upload.uploaded_at <= end_date)
            
            return query.order_by(desc(Upload.uploaded_at)).all()
            
        except Exception as e:
            logger.error(f"Erro ao obter uploads por período: {e}")
            return []
    
    def get_military_stats(self, upload_id: Optional[int] = None) -> Dict[str, Any]:
        """Obter estatísticas específicas dos dados militares"""
        try:
            from app.services.csv_service import CSVService
            from app.services.file_service import FileService
            import pandas as pd
            from pathlib import Path
            
            # Se não especificado, pegar o último upload
            if upload_id is None:
                upload = self.db.query(Upload).order_by(desc(Upload.uploaded_at)).first()
            else:
                upload = self.db.query(Upload).filter(Upload.id == upload_id).first()
            
            if not upload:
                return {}
            
            # Carregar dados do CSV
            file_service = FileService()
            csv_service = CSVService()
            file_path = file_service.get_file_path(upload.stored_path)
            
            # Carregar amostra dos dados
            df = csv_service.load_csv_preview(file_path, max_rows=10000)
            
            if df.empty:
                return {}
            
            stats = {}
            
            # 1. Distribuição por UF de nascimento
            if 'UF_NASCIMENTO' in df.columns:
                uf_counts = df['UF_NASCIMENTO'].value_counts().head(10)
                stats['uf_nascimento'] = {
                    'labels': uf_counts.index.tolist(),
                    'data': uf_counts.values.tolist()
                }
            
            # 2. Distribuição por sexo
            if 'SEXO' in df.columns:
                sexo_counts = df['SEXO'].value_counts()
                stats['sexo'] = {
                    'labels': sexo_counts.index.tolist(),
                    'data': sexo_counts.values.tolist()
                }
            
            # 3. Distribuição por estado civil
            if 'ESTADO_CIVIL' in df.columns:
                estado_civil_counts = df['ESTADO_CIVIL'].value_counts()
                stats['estado_civil'] = {
                    'labels': estado_civil_counts.index.tolist(),
                    'data': estado_civil_counts.values.tolist()
                }
            
            # 4. Distribuição por dispensa
            if 'DISPENSA' in df.columns:
                dispensa_counts = df['DISPENSA'].value_counts()
                stats['dispensa'] = {
                    'labels': dispensa_counts.index.tolist(),
                    'data': dispensa_counts.values.tolist()
                }
            
            # 5. Distribuição por zona residencial
            if 'ZONA_RESIDENCIAL' in df.columns:
                zona_counts = df['ZONA_RESIDENCIAL'].value_counts()
                stats['zona_residencial'] = {
                    'labels': zona_counts.index.tolist(),
                    'data': zona_counts.values.tolist()
                }
            
            # 6. Distribuição por escolaridade
            if 'ESCOLARIDADE' in df.columns:
                escolaridade_counts = df['ESCOLARIDADE'].value_counts().head(8)
                stats['escolaridade'] = {
                    'labels': escolaridade_counts.index.tolist(),
                    'data': escolaridade_counts.values.tolist()
                }
            
            # 7. Distribuição por ano de nascimento
            if 'ANO_NASCIMENTO' in df.columns:
                # Converter para int e filtrar valores válidos
                df['ANO_NASCIMENTO'] = pd.to_numeric(df['ANO_NASCIMENTO'], errors='coerce')
                df_clean = df.dropna(subset=['ANO_NASCIMENTO'])
                
                if not df_clean.empty:
                    # Agrupar por década
                    df_clean['DECADA'] = (df_clean['ANO_NASCIMENTO'] // 10) * 10
                    decada_counts = df_clean['DECADA'].value_counts().sort_index()
                    stats['ano_nascimento'] = {
                        'labels': [f"{int(d)}-{int(d)+9}" for d in decada_counts.index],
                        'data': decada_counts.values.tolist()
                    }
            
            # 8. Estatísticas físicas (se disponíveis)
            physical_stats = {}
            for col in ['PESO', 'ALTURA', 'CABECA', 'CALCADO', 'CINTURA']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    df_clean = df.dropna(subset=[col])
                    if not df_clean.empty:
                        physical_stats[col.lower()] = {
                            'media': float(df_clean[col].mean()),
                            'mediana': float(df_clean[col].median()),
                            'min': float(df_clean[col].min()),
                            'max': float(df_clean[col].max())
                        }
            
            if physical_stats:
                stats['estatisticas_fisicas'] = physical_stats
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas militares: {e}")
            return {}
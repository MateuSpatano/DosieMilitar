"""
Serviço de processamento de CSV
"""
import pandas as pd
import json
import chardet
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CSVService:
    """Serviço de processamento de arquivos CSV"""
    
    def __init__(self):
        self.encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        self.separators = [',', ';', '\t', '|']
        self.sample_size = 5000  # Linhas para amostra
        self.max_sample_rows = 100  # Máximo de linhas para preview
    
    def detect_encoding(self, file_path: Path) -> str:
        """Detectar encoding do arquivo"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                if result['confidence'] > 0.7:
                    return result['encoding']
        except Exception as e:
            logger.warning(f"Erro ao detectar encoding: {e}")
        
        # Fallback
        for encoding in self.encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1000)
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        return 'utf-8'
    
    def detect_separator(self, file_path: Path, encoding: str) -> str:
        """Detectar separador do CSV"""
        for sep in self.separators:
            try:
                df = pd.read_csv(file_path, sep=sep, encoding=encoding, nrows=5, on_bad_lines='skip')
                if len(df.columns) > 1:
                    return sep
            except Exception:
                continue
        
        return ','

    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """
        Obter informações do arquivo CSV

        Returns:
            Dict com: rows_total, cols_total, columns, dtypes, sample_rows
        """
        try:
            encoding = self.detect_encoding(file_path)
            separator = self.detect_separator(file_path, encoding)
            
            # Leitura da amostra
            df_sample = pd.read_csv(
                file_path,
                sep=separator,
                encoding=encoding,
                nrows=self.sample_size,
                on_bad_lines='skip'
            )
            
            rows_total = self._count_total_rows(file_path, separator, encoding)

            cols_total = len(df_sample.columns)
            columns = df_sample.columns.tolist()
            dtypes = self._detect_dtypes(df_sample)
            sample_rows = self._get_sample_rows(df_sample)

            return {
                'rows_total': rows_total,
                'cols_total': cols_total,
                'columns': columns,
                'dtypes': dtypes,
                'sample_rows': sample_rows
            }

        except Exception as e:
            logger.error(f"Erro ao processar CSV {file_path}: {e}")
            return {
                'rows_total': None,
                'cols_total': 0,
                'columns': [],
                'dtypes': {},
                'sample_rows': []
            }

    def _count_total_rows(self, file_path: Path, separator: str, encoding: str) -> int:
        """Contar total de linhas do arquivo"""
        try:
            if file_path.stat().st_size < 10 * 1024 * 1024:  # < 10MB
                df = pd.read_csv(file_path, sep=separator, encoding=encoding, on_bad_lines='skip')
                return len(df)

            total_rows = 0
            chunk_size = 10000
            for chunk in pd.read_csv(file_path, sep=separator, encoding=encoding, chunksize=chunk_size, on_bad_lines='skip'):
                total_rows += len(chunk)

            return total_rows

        except Exception as e:
            logger.warning(f"Erro ao contar linhas: {e}")
            return 0

    def _detect_dtypes(self, df: pd.DataFrame) -> Dict[str, str]:
        """Detectar tipos de dados simplificados"""
        dtype_map = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            if 'int' in dtype:
                dtype_map[col] = 'int'
            elif 'float' in dtype:
                dtype_map[col] = 'float'
            elif 'bool' in dtype:
                dtype_map[col] = 'bool'
            elif 'datetime' in dtype:
                dtype_map[col] = 'datetime'
            else:
                dtype_map[col] = 'string'
        return dtype_map

    def _get_sample_rows(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Obter amostra de linhas para preview"""
        sample_df = df.head(self.max_sample_rows)
        sample_rows = []
        for _, row in sample_df.iterrows():
            row_dict = {}
            for col, value in row.items():
                if pd.isna(value):
                    row_dict[col] = None
                else:
                    row_dict[col] = str(value)
            sample_rows.append(row_dict)
        return sample_rows

    def load_csv_preview(self, file_path: Path, max_rows: int = 100) -> pd.DataFrame:
        """Carregar preview do CSV com robustez contra erros de formatação"""
        try:
            encoding = self.detect_encoding(file_path)
            separator = self.detect_separator(file_path, encoding)

            return pd.read_csv(
                file_path,
                sep=separator,
                encoding=encoding,
                nrows=max_rows,
                on_bad_lines='skip'  # <- LINHAS MAL FORMADAS SÃO IGNORADAS
            )
        except Exception as e:
            logger.error(f"Erro ao carregar preview: {e}")
            return pd.DataFrame()
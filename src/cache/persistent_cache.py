"""
Sistema de caché persistente para DataFrames Excel.

Este módulo extiende el caché en memoria con persistencia en disco
para evitar recargas innecesarias entre sesiones.

Autor: Excel Chatbot
"""

import pandas as pd
import pickle
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import os
import hashlib
from config.logger_config import get_logger
from src.loader.excel_loader import infer_schema, ColumnSchema

logger = get_logger(__name__)

class PersistentDataFrameCache:
    """
    Caché persistente para DataFrames Excel.
    Guarda DataFrame y metadatos en disco para evitar recargas.
    """
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Estado en memoria
        self._dataframe: Optional[pd.DataFrame] = None
        self._file_path: Optional[str] = None
        self._schema: Optional[List[ColumnSchema]] = None
        self._file_stats: Optional[Dict[str, Any]] = None
        self._load_time: Optional[datetime] = None
        
        logger.info(f"📁 Caché persistente inicializado en: {self.cache_dir}")
    
    def _get_cache_key(self, file_path: str) -> str:
        """Genera clave única para el archivo."""
        # Usar hash del path absoluto
        abs_path = str(Path(file_path).resolve())
        return hashlib.md5(abs_path.encode()).hexdigest()[:16]
    
    def _get_cache_files(self, file_path: str) -> Dict[str, Path]:
        """Obtiene rutas de archivos de caché."""
        cache_key = self._get_cache_key(file_path)
        return {
            'dataframe': self.cache_dir / f"{cache_key}_df.pkl",
            'metadata': self.cache_dir / f"{cache_key}_meta.json",
            'schema': self.cache_dir / f"{cache_key}_schema.json"
        }
    
    def _save_to_disk(self, file_path: str, df: pd.DataFrame, schema: List[ColumnSchema]):
        """Guarda DataFrame y metadatos en disco."""
        try:
            cache_files = self._get_cache_files(file_path)
            
            # Guardar DataFrame
            logger.info("💾 Guardando DataFrame en caché persistente...")
            with open(cache_files['dataframe'], 'wb') as f:
                pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Guardar metadatos
            file_stats = os.stat(file_path)
            metadata = {
                'file_path': file_path,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'file_size': file_stats.st_size,
                'file_mtime': file_stats.st_mtime,
                'cache_time': datetime.now().isoformat(),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            }
            
            with open(cache_files['metadata'], 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Guardar esquema
            schema_data = [
                {
                    'name': col['name'],
                    'dtype': col['dtype'],
                    'sample_values': col['sample_values']
                }
                for col in schema
            ]
            
            with open(cache_files['schema'], 'w') as f:
                json.dump(schema_data, f, indent=2)
            
            logger.info(f"✅ Caché guardado en disco: {len(df):,} filas, {len(df.columns)} columnas")
            
        except Exception as e:
            logger.error(f"❌ Error guardando caché: {e}")
    
    def _load_from_disk(self, file_path: str) -> bool:
        """Carga DataFrame y metadatos desde disco."""
        try:
            cache_files = self._get_cache_files(file_path)
            
            # Verificar que todos los archivos existen
            if not all(f.exists() for f in cache_files.values()):
                logger.debug("Archivos de caché no encontrados")
                return False
            
            # Verificar si el archivo original ha cambiado
            with open(cache_files['metadata'], 'r') as f:
                cached_metadata = json.load(f)
            
            current_stats = os.stat(file_path)
            if (current_stats.st_size != cached_metadata['file_size'] or 
                current_stats.st_mtime != cached_metadata['file_mtime']):
                logger.info("📄 Archivo modificado, caché obsoleto")
                return False
            
            logger.info("📂 Cargando DataFrame desde caché persistente...")
            start_time = datetime.now()
            
            # Cargar DataFrame
            with open(cache_files['dataframe'], 'rb') as f:
                df = pickle.load(f)
            
            # Cargar esquema
            with open(cache_files['schema'], 'r') as f:
                schema_data = json.load(f)
                schema: List[ColumnSchema] = [
                    ColumnSchema(
                        name=col['name'],
                        dtype=col['dtype'],
                        sample_values=col['sample_values']
                    )
                    for col in schema_data
                ]
            
            # Actualizar estado en memoria
            self._dataframe = df
            self._file_path = file_path
            self._schema = schema
            self._file_stats = {
                'size': current_stats.st_size,
                'mtime': current_stats.st_mtime
            }
            self._load_time = datetime.now()
            
            load_duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ DataFrame cargado desde caché:")
            logger.info(f"   - Filas: {len(df):,}")
            logger.info(f"   - Columnas: {len(df.columns)}")
            logger.info(f"   - Tiempo desde caché: {load_duration:.2f} segundos")
            
            print(f"📂 DataFrame cargado desde caché: {len(df):,} filas, {len(df.columns)} columnas")
            print(f"⚡ Tiempo de carga: {load_duration:.2f} segundos")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cargando desde caché: {e}")
            return False
    
    def is_loaded(self) -> bool:
        """Verifica si hay un DataFrame cargado."""
        return self._dataframe is not None
    
    def get_current_file(self) -> Optional[str]:
        """Obtiene la ruta del archivo actualmente cargado."""
        return self._file_path
    
    def load_dataframe(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        Carga el DataFrame con caché persistente.
        
        Args:
            file_path: Ruta al archivo Excel
            sheet_name: Nombre de la hoja (opcional)
            
        Returns:
            pd.DataFrame: DataFrame cargado
        """
        # Verificar si ya está cargado
        if (self._dataframe is not None and 
            self._file_path == file_path):
            logger.info("✅ DataFrame ya está en memoria")
            return self._dataframe
        
        # Intentar cargar desde caché persistente
        if self._load_from_disk(file_path):
            return self._dataframe  # type: ignore
        
        # Si no hay caché, cargar desde Excel
        logger.info(f"📊 Cargando DataFrame desde Excel: {file_path}")
        start_time = datetime.now()
        
        # Verificar que el archivo existe
        excel_path = Path(file_path)
        if not excel_path.exists():
            raise FileNotFoundError(f"Archivo Excel no encontrado: {file_path}")
        
        try:
            # Cargar DataFrame
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            # Generar esquema
            schema = infer_schema(df)
            
            # Actualizar estado en memoria
            self._dataframe = df
            self._file_path = file_path
            self._schema = schema
            self._load_time = datetime.now()
            
            file_stats = os.stat(file_path)
            self._file_stats = {
                'size': file_stats.st_size,
                'mtime': file_stats.st_mtime
            }
            
            load_duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ DataFrame cargado desde Excel:")
            logger.info(f"   - Filas: {len(df):,}")
            logger.info(f"   - Columnas: {len(df.columns)}")
            logger.info(f"   - Tiempo de carga: {load_duration:.2f} segundos")
            
            print(f"📊 DataFrame cargado: {len(df):,} filas, {len(df.columns)} columnas")
            print(f"⏱️  Tiempo de carga: {load_duration:.2f} segundos")
            
            # Guardar en caché persistente para la próxima vez
            self._save_to_disk(file_path, df, schema)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error cargando DataFrame: {e}")
            raise ValueError(f"Error al cargar Excel: {e}")
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Obtiene el DataFrame cacheado."""
        return self._dataframe
    
    def get_schema(self) -> Optional[List[ColumnSchema]]:
        """Obtiene el esquema del DataFrame cacheado."""
        return self._schema
    
    def get_schema_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del esquema para enviar a Groq.
        Solo incluye información estructural, NO DATOS.
        """
        if not self.is_loaded() or self._dataframe is None:
            return {}
        
        df = self._dataframe
        
        # SOLO información estructural - NO DATOS
        summary = {
            'file_path': self._file_path,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'load_time': self._load_time.isoformat() if self._load_time else None
        }
        
        # SOLO primeras 2 filas como ejemplo de estructura (no para análisis)
        if len(df) > 0:
            sample_size = min(2, len(df))
            summary['sample_structure'] = df.head(sample_size).to_dict('records')
        
        # Información de tipos de columnas (sin valores)
        if self._schema:
            summary['column_info'] = [
                {
                    'name': col['name'],
                    'dtype': col['dtype'],
                    'sample_values': col['sample_values'][:2]  # Solo 2 valores de ejemplo
                }
                for col in self._schema
            ]
        
        return summary
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché."""
        if not self.is_loaded() or self._dataframe is None:
            return {'loaded': False}
        
        df = self._dataframe
        cache_files = self._get_cache_files(self._file_path or "")
        
        return {
            'loaded': True,
            'file_path': self._file_path,
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'load_time': self._load_time.isoformat() if self._load_time else None,
            'file_size_mb': self._file_stats['size'] / 1024 / 1024 if self._file_stats else None,
            'has_disk_cache': all(f.exists() for f in cache_files.values()),
            'cache_files': [str(f) for f in cache_files.values()]
        }
    
    def clear_cache(self, remove_disk_cache: bool = False):
        """
        Limpia el caché.
        
        Args:
            remove_disk_cache: Si True, también elimina archivos de disco
        """
        logger.info("🧹 Limpiando caché del DataFrame")
        
        # Limpiar memoria
        self._dataframe = None
        self._file_path = None
        self._schema = None
        self._file_stats = None
        self._load_time = None
        
        # Limpiar disco si se solicita
        if remove_disk_cache:
            try:
                for cache_file in self.cache_dir.glob("*"):
                    if cache_file.is_file():
                        cache_file.unlink()
                        logger.info(f"🗑️  Eliminado: {cache_file}")
            except Exception as e:
                logger.error(f"❌ Error limpiando caché de disco: {e}")
    
    def clean_old_cache_files(self, max_age_days: int = 7):
        """Limpia archivos de caché antiguos."""
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)
            cleaned = 0
            
            for cache_file in self.cache_dir.glob("*"):
                if cache_file.is_file() and cache_file.stat().st_mtime < cutoff_time:
                    cache_file.unlink()
                    cleaned += 1
                    logger.info(f"🗑️  Eliminado caché antiguo: {cache_file}")
            
            if cleaned > 0:
                logger.info(f"🧹 Limpiados {cleaned} archivos de caché antiguos")
            
        except Exception as e:
            logger.error(f"❌ Error limpiando caché antiguo: {e}")

# Instancia global del caché persistente
persistent_cache = PersistentDataFrameCache()

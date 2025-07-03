"""
Script de limpieza automática para el chatbot Excel.

Este script limpia archivos obsoletos y mantiene el sistema optimizado.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from src.cache.persistent_cache import persistent_cache
from config.logger_config import get_logger

logger = get_logger(__name__)

def clean_old_cache_files(max_age_days: int = 7):
    """Limpia archivos de caché antiguos."""
    try:
        persistent_cache.clean_old_cache_files(max_age_days)
        logger.info(f"✅ Limpieza de caché completada (archivos > {max_age_days} días)")
    except Exception as e:
        logger.error(f"❌ Error en limpieza de caché: {e}")

def clean_old_log_files(max_age_days: int = 30):
    """Limpia archivos de log antiguos."""
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return
        
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        cleaned = 0
        
        for log_file in logs_dir.glob("*.log*"):
            if log_file.is_file():
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_time:
                    log_file.unlink()
                    cleaned += 1
                    logger.info(f"🗑️  Eliminado log antiguo: {log_file}")
        
        if cleaned > 0:
            logger.info(f"🧹 Limpiados {cleaned} archivos de log antiguos")
    
    except Exception as e:
        logger.error(f"❌ Error limpiando logs: {e}")

def clean_pycache():
    """Limpia archivos __pycache__."""
    try:
        cleaned = 0
        for root, dirs, files in os.walk("."):
            if "__pycache__" in dirs:
                pycache_path = Path(root) / "__pycache__"
                shutil.rmtree(pycache_path)
                cleaned += 1
                logger.info(f"🗑️  Eliminado: {pycache_path}")
        
        if cleaned > 0:
            logger.info(f"🧹 Limpiados {cleaned} directorios __pycache__")
    
    except Exception as e:
        logger.error(f"❌ Error limpiando __pycache__: {e}")

def main():
    """Ejecuta limpieza completa."""
    print("🧹 LIMPIEZA AUTOMÁTICA DEL SISTEMA")
    print("=" * 50)
    
    # Limpiar caché antiguo
    print("📂 Limpiando caché antiguo...")
    clean_old_cache_files(7)
    
    # Limpiar logs antiguos
    print("📄 Limpiando logs antiguos...")
    clean_old_log_files(30)
    
    # Limpiar __pycache__
    print("🐍 Limpiando archivos Python temporales...")
    clean_pycache()
    
    print("✅ Limpieza completada")

if __name__ == "__main__":
    main()

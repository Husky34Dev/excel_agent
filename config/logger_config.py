import logging
import sys
from pathlib import Path
from logging import Logger
from logging.handlers import RotatingFileHandler

def get_file_handler(
    log_file: str = "logs/excel_chatbot.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> RotatingFileHandler:
    """
    Crea un handler para escribir logs a archivo con rotación.
    """
    # Crear directorio si no existe
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)
    
    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    
    return handler

def configure_logging(
    level: str = "INFO",
    fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt: str = "%Y-%m-%d %H:%M:%S"
) -> Logger:
    """
    Configura el logging global de la aplicación con salida a terminal y archivo.
    """
    # Configurar logging con terminal y archivo
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt,
        datefmt=datefmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
            get_file_handler()
        ]
    )
    
    logger = logging.getLogger()
    logger.debug("Logging configurado: nivel=%s", level)
    return logger

def configure_file_only_logging(
    level: str = "INFO",
    log_file: str = "logs/excel_chatbot.log"
) -> Logger:
    """
    Configura logging solo a archivo, sin salida a terminal.
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        handlers=[get_file_handler(log_file)],
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True
    )
    
    # Silenciar logs de librerías externas en terminal
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("groq").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    logger = logging.getLogger()
    logger.info(f"Logging configurado solo a archivo: {log_file}")
    return logger

def get_logger(name: str) -> Logger:
    """
    Obtiene un logger nombrado usando la configuración global.
    """
    return logging.getLogger(name)

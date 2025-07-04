from pydantic_settings import BaseSettings
from pydantic import Field
import os
from pathlib import Path

class Settings(BaseSettings):
    """Configuración de la aplicación desde variables de entorno."""
    # Groq Cloud
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"

    # Sandbox limits
    sandbox_cpu_time: int = 2
    sandbox_memory_bytes: int = 200 * 1024 * 1024
    sandbox_user: str = "nobody"
    sandbox_temp_dir: str

    # Excel
    excel_default_sheet: str = "0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Crear directorio de sandbox si no existe
        Path(self.sandbox_temp_dir).mkdir(exist_ok=True)

def get_settings() -> Settings:
    """Devuelve una instancia singleton de Settings."""
    return Settings()
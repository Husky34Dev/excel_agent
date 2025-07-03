import pandas as pd
from pathlib import Path
from typing import Optional
from src.executor.sandbox_executor import SandboxExecutor
from config.settings import get_settings
from config.logger_config import get_logger

logger = get_logger(__name__)

class PythonExecTool:
    """
    Herramienta para ejecutar código Python con un DataFrame precargado.
    """
    def __init__(self, excel_path: Optional[str] = None):
        self.settings = get_settings()
        self.excel_path = excel_path or "data/input/demo.xlsx"
        
        # Verificar que el archivo existe
        if not Path(self.excel_path).exists():
            raise FileNotFoundError(f"Archivo Excel no encontrado: {self.excel_path}")
            
        self.sandbox = SandboxExecutor(
            cpu_time=self.settings.sandbox_cpu_time,
            memory_bytes=self.settings.sandbox_memory_bytes,
            user_name=self.settings.sandbox_user
        )
        
        # Prefijo con carga del DataFrame
        self._code_prefix = (
            "import pandas as pd\n"
            f"df = pd.read_excel('{self.excel_path}')\n"
        )
        logger.debug(f"PythonExecTool inicializado con archivo: {self.excel_path}")

    def execute(self, code: str) -> str:
        """
        Ejecuta código Python con DataFrame precargado.
        
        Args:
            code: Código Python que puede usar la variable 'df'
            
        Returns:
            str: Salida estándar (stdout)
            
        Raises:
            RuntimeError: Si hay errores en stderr
        """
        full_code = self._code_prefix + code
        logger.debug(f"Ejecutando código: {code[:100]}...")
        
        stdout, stderr = self.sandbox.execute_code(full_code)
        if stderr:
            logger.error(f"Error en ejecución: {stderr}")
            raise RuntimeError(f"python_exec error: {stderr.strip()}")
        
        logger.debug(f"Ejecución exitosa, salida: {stdout[:100]}...")
        return stdout

# Función de conveniencia para compatibilidad
def python_exec(code: str, excel_path: Optional[str] = None) -> str:
    """
    Ejecuta un fragmento de código Python en un entorno donde 'df' ya está cargado.

    Args:
        code (str): Código Python que puede usar la variable 'df'.
        excel_path (str, optional): Ruta al archivo Excel. Si es None, usa el default.

    Returns:
        str: Salida estándar (stdout).

    Raises:
        RuntimeError: Si hay errores en stderr.
    """
    tool = PythonExecTool(excel_path)
    return tool.execute(code)

import json
from typing import Any
from config.logger_config import get_logger

logger = get_logger(__name__)

class CodeAgentError(Exception):
    """Excepción base para errores del CodeAgent."""
    pass

class ExecutionError(CodeAgentError):
    """Error en la ejecución dentro del sandbox."""
    def __init__(self, stderr: str):
        super().__init__(f"Error en sandbox executor: {stderr}")
        self.stderr = stderr

class PromptError(CodeAgentError):
    """Error al crear o enviar el prompt al modelo LLM."""
    pass

class LoaderError(CodeAgentError):
    """Error al cargar archivos Excel."""
    pass

def parse_output(stdout: str) -> Any:
    """
    Intenta parsear stdout como JSON, si no devuelve la cadena cruda.
    Maneja problemas de codificación comunes en Windows.
    
    Args:
        stdout: Salida estándar del código ejecutado
        
    Returns:
        Any: Objeto parseado si es JSON válido, string crudo caso contrario
        
    Example:
        >>> parse_output('{"result": 42}')
        {'result': 42}
        >>> parse_output('Plain text output')
        'Plain text output'
    """
    if not stdout or not stdout.strip():
        logger.debug("stdout vacío, retornando string vacío")
        return ""
    
    # Limpiar stdout y manejar problemas de codificación
    clean_stdout = stdout.strip()
    
    # Intentar corregir problemas comunes de codificación UTF-8 en Windows
    try:
        # Si hay caracteres mal codificados, intentar decodificar correctamente
        if any(char in clean_stdout for char in ['Ã¡', 'Ã©', 'Ã­', 'Ã³', 'Ã¹', 'Ã±', 'Ã¼', 'Ã§', 'Ãº']):
            # Problemas comunes de latin-1 -> utf-8
            replacements = {
                'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ã¹': 'ú',
                'Ã±': 'ñ', 'Ã¼': 'ü', 'Ã§': 'ç', 'Ãº': 'ú',
                'NÃºmero': 'Número', 'Ãºnicos': 'únicos', 'regiÃ³n': 'región'
            }
            for bad, good in replacements.items():
                clean_stdout = clean_stdout.replace(bad, good)
            logger.debug("Corregidos problemas de codificación en stdout")
    except Exception as e:
        logger.debug(f"Error corrigiendo codificación: {e}")
    
    try:
        # Intentar parsear como JSON
        result = json.loads(clean_stdout)
        logger.debug(f"stdout parseado como JSON: {type(result)}")
        return result
    except json.JSONDecodeError:
        # Si no es JSON válido, retornar texto crudo
        logger.debug("stdout no es JSON válido, retornando como texto")
        return clean_stdout
    except Exception as e:
        # En caso de cualquier otro error, loggear y retornar texto
        logger.warning(f"Error inesperado al parsear stdout: {e}")
        return clean_stdout

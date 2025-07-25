import subprocess
import tempfile
import os
import sys
import platform
import ast
import re
import pickle
from pathlib import Path
from typing import Set, List, Optional
import pandas as pd
from config.settings import get_settings
from config.logger_config import get_logger

# Solo importar resource y pwd en sistemas Unix
if platform.system() != 'Windows':
    import resource
    import pwd

logger = get_logger(__name__)

class SecurityError(Exception):
    """Error de seguridad en validación de código."""
    pass

class SandboxExecutor:
    """
    Ejecuta código Python en un proceso aislado con límites.
    Compatible con Windows y sistemas Unix.
    Incluye validación de imports para mayor seguridad.
    Soporta pre-inyección de DataFrames para mejor rendimiento.
    """
    
    # Imports permitidos (whitelist)
    ALLOWED_IMPORTS = {
        'pandas', 'pd',
        'numpy', 'np', 
        'datetime',
        'json',
        'math',
        'statistics',
        'collections',
        're',
        'itertools',
        'functools',
        'operator'
    }
    
    # Imports prohibidos explícitamente (blacklist adicional)
    FORBIDDEN_IMPORTS = {
        'os', 'sys', 'subprocess', 'shutil', 'glob',
        'socket', 'urllib', 'requests', 'http',
        'ftplib', 'smtplib', 'telnetlib',
        'pickle', 'marshal', 'shelve',
        'sqlite3', 'mysql', 'psycopg2',
        'exec', 'eval', 'compile', '__import__',
        'open', 'file', 'input', 'raw_input',
        'importlib', 'pkgutil', 'imp'
    }
    
    # Funciones peligrosas
    FORBIDDEN_FUNCTIONS = {
        'exec', 'eval', 'compile', '__import__',
        'open', 'file', 'input', 'raw_input',
        'getattr', 'setattr', 'delattr', 'hasattr',
        'globals', 'locals', 'vars', 'dir'
    }

    def __init__(
        self, 
        cpu_time: int = 2, 
        memory_bytes: int = 200*1024*1024, 
        user_name: str = "nobody"
    ):
        self.cpu_time = cpu_time
        self.memory_bytes = memory_bytes
        self.user_name = user_name
        self.is_windows = platform.system() == 'Windows'
        
        # Obtener directorio temporal de configuración
        settings = get_settings()
        self.temp_dir = Path(settings.sandbox_temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        
        if not self.is_windows:
            try:
                self.uid = pwd.getpwnam(user_name).pw_uid # type: ignore
                logger.debug(f"Usuario sandbox configurado: {user_name} (UID: {self.uid})")
            except (KeyError, NameError):
                logger.warning(f"Usuario '{user_name}' no encontrado, ejecutando como usuario actual")
                self.uid = None
        else:
            logger.debug("Ejecutando en Windows, sin restricciones de usuario")
            self.uid = None
        
        self._injected_dataframe_path: Optional[str] = None
        
        # Auto-limpiar archivos antiguos al inicializar
        self._cleanup_old_files()
    
    def _cleanup_old_files(self) -> None:
        """Limpia archivos temporales antiguos del sandbox."""
        try:
            import time
            current_time = time.time()
            
            # Eliminar archivos más antiguos de 1 hora
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > 3600:  # 1 hora
                        try:
                            file_path.unlink()
                            logger.debug(f"Archivo temporal antiguo eliminado: {file_path.name}")
                        except:
                            pass  # Ignorar errores de limpieza
        except Exception as e:
            logger.debug(f"Error en limpieza automática: {e}")
    
    def inject_dataframe(self, df: pd.DataFrame) -> None:
        """
        Pre-inyecta un DataFrame que estará disponible como 'df' en todas las ejecuciones.
        
        Args:
            df: DataFrame a inyectar
        """
        try:
            # Crear archivo pickle temporal para el DataFrame
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl', dir=self.temp_dir) as tmp_file:
                pickle.dump(df, tmp_file)
                self._injected_dataframe_path = tmp_file.name
            
            logger.debug(f"DataFrame inyectado exitosamente: {df.shape[0]} filas, {df.shape[1]} columnas")
            
        except Exception as e:
            logger.error(f"Error inyectando DataFrame: {e}")
            raise
    
    def clear_injected_dataframe(self) -> None:
        """Limpia el DataFrame inyectado."""
        if self._injected_dataframe_path and os.path.exists(self._injected_dataframe_path):
            try:
                os.unlink(self._injected_dataframe_path)
                self._injected_dataframe_path = None
                logger.debug("DataFrame inyectado limpiado")
            except Exception as e:
                logger.warning(f"Error limpiando DataFrame inyectado: {e}")
    
    def _get_setup_code(self) -> str:
        """
        Genera el código de setup que carga el DataFrame inyectado.
        
        Returns:
            str: Código de setup
        """
        if not self._injected_dataframe_path:
            return """
import pandas as pd
import numpy as np
from datetime import datetime
"""
        
        return f"""
import pandas as pd
import numpy as np
import pickle
from datetime import datetime

# Cargar DataFrame pre-inyectado
with open(r'{self._injected_dataframe_path}', 'rb') as f:
    df = pickle.load(f)
"""
    
    def _validate_imports(self, code: str) -> None:
        """
        Valida que el código solo use imports permitidos.
        
        Args:
            code: Código Python a validar
            
        Raises:
            SecurityError: Si se detectan imports no permitidos
        """
        # Buscar imports con regex (método rápido)
        import_patterns = [
            r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_\.]*)',
            r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_\.]*)\s+import',
        ]
        
        found_imports = set()
        
        for line in code.split('\n'):
            for pattern in import_patterns:
                match = re.match(pattern, line)
                if match:
                    module = match.group(1).split('.')[0]  # Solo el módulo principal
                    found_imports.add(module)
        
        # Verificar imports prohibidos explícitamente
        forbidden_found = found_imports.intersection(self.FORBIDDEN_IMPORTS)
        if forbidden_found:
            raise SecurityError(f"Imports prohibidos detectados: {', '.join(forbidden_found)}")
        
        # Verificar que solo use imports permitidos
        not_allowed = found_imports - self.ALLOWED_IMPORTS
        if not_allowed:
            raise SecurityError(f"Imports no permitidos: {', '.join(not_allowed)}. "
                              f"Permitidos: {', '.join(sorted(self.ALLOWED_IMPORTS))}")
        
        logger.debug(f"Imports validados: {', '.join(found_imports)}")

    def _validate_functions(self, code: str) -> None:
        """
        Valida que el código no use funciones peligrosas.
        
        Args:
            code: Código Python a validar
            
        Raises:
            SecurityError: Si se detectan funciones peligrosas
        """
        # Buscar funciones peligrosas
        for func in self.FORBIDDEN_FUNCTIONS:
            # Buscar llamadas a la función
            pattern = rf'\b{re.escape(func)}\s*\('
            if re.search(pattern, code):
                raise SecurityError(f"Función prohibida detectada: {func}()")
        
        # Verificar patrones peligrosos adicionales
        dangerous_patterns = [
            (r'__.*__', "Uso de métodos dunder prohibido"),
            (r'\.system\s*\(', "Llamada a system() prohibida"),
            (r'\.popen\s*\(', "Llamada a popen() prohibida"),
            (r'\.call\s*\(', "Llamada a call() prohibida"),
        ]
        
        for pattern, message in dangerous_patterns:
            if re.search(pattern, code):
                raise SecurityError(message)
        
        logger.debug("Validación de funciones completada")

    def _validate_ast(self, code: str) -> None:
        """
        Validación adicional usando AST (Abstract Syntax Tree).
        
        Args:
            code: Código Python a validar
            
        Raises:
            SecurityError: Si se detectan patrones peligrosos
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SecurityError(f"Error de sintaxis en el código: {e}")
        
        # Verificar nodos peligrosos
        for node in ast.walk(tree):
            # Prohibir llamadas a exec/eval
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.FORBIDDEN_FUNCTIONS:
                        raise SecurityError(f"Llamada prohibida detectada: {node.func.id}")
            
            # Prohibir acceso a atributos privados
            if isinstance(node, ast.Attribute):
                if node.attr.startswith('_'):
                    raise SecurityError(f"Acceso a atributo privado prohibido: {node.attr}")
        
        logger.debug("Validación AST completada")

    def validate_code(self, code: str) -> None:
        """
        Ejecuta todas las validaciones de seguridad en el código.
        
        Args:
            code: Código Python a validar
            
        Raises:
            SecurityError: Si el código no pasa las validaciones
        """
        logger.debug("Iniciando validación de seguridad del código")
        
        # 1. Validar imports
        self._validate_imports(code)
        
        # 2. Validar funciones
        self._validate_functions(code)
        
        # 3. Validar AST
        self._validate_ast(code)
        
        logger.info("✅ Código validado exitosamente - sin amenazas detectadas")

    def _preexec_unix(self):
        """Configuración previa a la ejecución en sistemas Unix."""
        if not self.is_windows and 'resource' in globals() and 'pwd' in globals():
            if self.uid is not None:
                os.setuid(self.uid) # type: ignore
            resource.setrlimit(resource.RLIMIT_CPU, (self.cpu_time, self.cpu_time)) # type: ignore
            resource.setrlimit(resource.RLIMIT_AS, (self.memory_bytes, self.memory_bytes)) # type: ignore

    def execute_code(self, code: str, timeout: int = 5):
        """
        Ejecuta código Python en un entorno aislado.
        Incluye validación de seguridad antes de la ejecución.
        
        Args:
            code: Código Python a ejecutar
            timeout: Tiempo límite en segundos
            
        Returns:
            tuple: (stdout, stderr)
        """
        # VALIDACIÓN DE SEGURIDAD ANTES DE EJECUTAR
        try:
            self.validate_code(code)
        except SecurityError as e:
            error_msg = f"🛡️ CÓDIGO RECHAZADO POR SEGURIDAD: {str(e)}"
            logger.error(error_msg)
            return "", error_msg
        
        # Crear archivo temporal en el directorio configurado
        script_path = self.temp_dir / f"script_{os.getpid()}.py"
        
        try:
            # Escribir código al archivo
            setup_code = self._get_setup_code()
            full_code = f"{setup_code}\n{code}"
            script_path.write_text(full_code, encoding='utf-8')
            
            # Preparar comando y configuración según el SO
            # Usar el Python del entorno virtual actual
            python_executable = sys.executable
            cmd = [python_executable, str(script_path)]
            preexec_fn = None if self.is_windows else self._preexec_unix
            
            # Configurar entorno limpio para evitar conflictos con uvicorn
            env = os.environ.copy()
            if self.is_windows:
                # Configuración robusta para Windows con manejo correcto de UTF-8
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONUNBUFFERED'] = '1'
                env['PYTHONUTF8'] = '1'
                env['LC_ALL'] = 'es_ES.UTF-8'
                env['LANG'] = 'es_ES.UTF-8'
                # Evitar conflictos con el reloader de uvicorn
                env.pop('UVICORN_RELOAD', None)
                env.pop('UVICORN_RELOAD_DIRS', None)
            
            logger.debug(f"Ejecutando código validado en {script_path}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout,
                preexec_fn=preexec_fn,
                env=env,
                stdin=subprocess.DEVNULL,
                # Crear un grupo de procesos separado en Windows
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if self.is_windows else 0
            )
            
            logger.debug(f"Ejecución completada. Código de salida: {result.returncode}")
            return result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout después de {timeout} segundos"
            logger.error(error_msg)
            return "", error_msg
        except Exception as e:
            error_msg = f"Error ejecutando código: {str(e)}"
            logger.error(error_msg)
            return "", error_msg
        finally:
            # Limpiar archivo temporal
            if script_path.exists():
                script_path.unlink()
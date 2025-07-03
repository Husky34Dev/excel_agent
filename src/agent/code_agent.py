import os
from typing import List, Any, Optional, Dict
from groq import Groq
import logging
from src.loader.excel_loader import load_excel, load_all_sheets, infer_schema, SheetInfo
from src.prompt.prompt_builder import build_prompt
from src.prompt.multi_sheet_prompt_builder import build_multi_sheet_prompt, build_single_sheet_prompt
from src.executor.sandbox_executor import SandboxExecutor
from src.utils import ExecutionError, PromptError, parse_output
from config.logger_config import get_logger

# Inicializar logger
logger = get_logger(__name__)

class CodeAgent:
    """
    Orquesta carga, prompt, generación y ejecución de código.
    Soporta análisis de una hoja específica o todas las hojas automáticamente.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile",
        cpu_time: int = 2,
        memory_bytes: int = 200 * 1024 * 1024,
        sandbox_user: str = "nobody",
        use_all_sheets: bool = True  # NUEVO: Por defecto usa todas las hojas
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY no está definida.")
        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.sandbox = SandboxExecutor(cpu_time=cpu_time, memory_bytes=memory_bytes, user_name=sandbox_user)
        self.use_all_sheets = use_all_sheets
        logger.debug("CodeAgent inicializado con modelo: %s, modo multi-hoja: %s", self.model, use_all_sheets)

    def generate_code(self, prompt: str) -> str:
        """
        Genera código Python usando el API de Groq.

        Args:
            prompt: Texto de entrada para generación.
        Raises:
            PromptError: Si la llamada al API falla.
        Returns:
            str: Código Python generado.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un agente experto que genera código Python con pandas para analizar datos de Excel. Puedes trabajar con archivos de una sola hoja o múltiples hojas según sea necesario."},
                    {"role": "user",   "content": prompt}
                ],
                stream=False
            )
        except Exception as e:
            logger.error("Error generando código: %s", e)
            raise PromptError(str(e))
        # Asegurar que content no sea None antes de strip
        content = response.choices[0].message.content or ""
        code = content.strip()
        # Eliminar delimitadores Markdown si existen
        code = code.replace("```python", "").replace("```", "").strip()
        
        # Reemplazar placeholder de ruta del Excel con la ruta real
        # Esto se hará en el método ask() donde tenemos acceso a excel_path
        
        logger.debug("Código generado: %s", code)
        return code

    def ask(self, excel_path: str, question: str, specific_sheet: Optional[str] = None) -> Any:
        """
        Procesa una pregunta sobre un archivo Excel y devuelve el resultado.
        Automáticamente detecta si usar una hoja específica o todas las hojas.

        Args:
            excel_path: Ruta al archivo .xlsx.
            question: Pregunta o consulta para el agente.
            specific_sheet: Si se especifica, usa solo esa hoja (ignora use_all_sheets)
        Raises:
            ExecutionError: Si la ejecución del código falla.
            PromptError: Si la generación de código falla.
        Returns:
            Any: Resultado parseado o texto crudo.
        """
        
        if specific_sheet:
            # Modo hoja específica
            logger.info("Cargando hoja específica '%s' desde %s", specific_sheet, excel_path)
            df = load_excel(excel_path, sheet_name=specific_sheet)
            schema = infer_schema(df)
            prompt = build_single_sheet_prompt(schema, question, excel_path)
            code = self.generate_code(prompt)
            
        elif self.use_all_sheets:
            # Modo todas las hojas (NUEVO comportamiento por defecto)
            logger.info("Cargando TODAS las hojas desde %s", excel_path)
            all_sheets = load_all_sheets(excel_path)
            
            # Mostrar resumen de hojas cargadas
            sheet_names = list(all_sheets.keys())
            logger.info("Hojas cargadas: %s", sheet_names)
            print(f"📊 Cargadas {len(all_sheets)} hojas: {', '.join(sheet_names)}")
            
            prompt = build_multi_sheet_prompt(all_sheets, question, excel_path)
            code = self.generate_code(prompt)
            
        else:
            # Modo hoja única (comportamiento original)
            logger.info("Cargando Excel desde %s (modo hoja única)", excel_path)
            df = load_excel(excel_path)
            schema = infer_schema(df)
            prompt = build_single_sheet_prompt(schema, question, excel_path)
            code = self.generate_code(prompt)
        
        # Ejecutar código
        stdout, stderr = self.sandbox.execute_code(code)
        if stderr:
            logger.error("Error en sandbox: %s", stderr)
            raise ExecutionError(stderr)
        
        result = parse_output(stdout)
        logger.info("Ejecución completada, resultado: %s", result)
        return result

    def ask_single_sheet(self, excel_path: str, question: str, sheet_name: Optional[str] = None) -> Any:
        """
        Método específico para consultas de una sola hoja.
        
        Args:
            excel_path: Ruta al archivo Excel
            question: Pregunta del usuario
            sheet_name: Nombre específico de la hoja (opcional)
            
        Returns:
            Resultado del análisis
        """
        return self.ask(excel_path, question, specific_sheet=sheet_name)

    def ask_multi_sheet(self, excel_path: str, question: str) -> Any:
        """
        Método específico para consultas que pueden abarcar múltiples hojas.
        
        Args:
            excel_path: Ruta al archivo Excel
            question: Pregunta del usuario
            
        Returns:
            Resultado del análisis
        """
        # Temporalmente forzar modo multi-hoja
        original_mode = self.use_all_sheets
        self.use_all_sheets = True
        try:
            result = self.ask(excel_path, question)
            return result
        finally:
            self.use_all_sheets = original_mode

    def generate_code_batch(self, prompts: List[str]) -> List[str]:
        """
        Genera múltiples fragmentos de código en lote.

        Args:
            prompts: Lista de textos de entrada.
        Returns:
            List[str]: Códigos generados para cada prompt.
        """
        return [self.generate_code(p) for p in prompts]

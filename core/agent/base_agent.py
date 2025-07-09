"""
Agente base modular con soporte para configuración de clientes.

Este agente extiende SimpleCachedCodeAgent añadiendo:
1. Integración con configuración de clientes
2. Prompts personalizados por dominio
3. Gestión de datos por workspace
4. Sistema modular y extensible

Autor: Excel Agent
"""

import os
from typing import Any, Optional, Dict
from groq import Groq
import logging
from core.cache.persistent_cache import persistent_cache
from core.executor.sandbox_executor import SandboxExecutor
from core.client_manager import ClientConfig
from utils import ExecutionError, PromptError, parse_output
from config.logger_config import get_logger

logger = get_logger(__name__)

class BaseAgent:
    """
    Agente base modular que integra configuración de clientes.
    
    Estrategia:
    1. Precarga DataFrame completo UNA VEZ
    2. Lo mantiene en memoria para todas las consultas
    3. Usa prompts personalizados por cliente/dominio
    4. Ejecuta código generado localmente sobre el DataFrame cacheado
    """
    
    def __init__(
        self,
        client_config: ClientConfig,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile",
        cpu_time: int = 5,
        memory_bytes: int = 200 * 1024 * 1024,
        sandbox_user: str = "nobody"
    ):
        """
        Inicializa el agente con configuración de cliente.
        
        Args:
            client_config: Configuración del cliente
            api_key: Clave API de Groq
            model: Modelo de Groq a usar
            cpu_time: Tiempo máximo de CPU para sandbox
            memory_bytes: Memoria máxima para sandbox
            sandbox_user: Usuario para sandbox
        """
        self.client_config = client_config
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY no está definida.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.sandbox = SandboxExecutor(
            cpu_time=cpu_time, 
            memory_bytes=memory_bytes, 
            user_name=sandbox_user
        )
        
        logger.info(f"✅ BaseAgent inicializado para cliente: {client_config.client_name}")
        logger.info(f"   Modelo: {model}")
        logger.info(f"   Workspace: {client_config.get_workspace_folder()}")
    
    def preload_dataframe(self, excel_path: str, sheet_name: Optional[str] = None) -> bool:
        """
        Precarga el DataFrame en caché y lo inyecta en el sandbox.
        
        Args:
            excel_path: Ruta al archivo Excel
            sheet_name: Nombre de la hoja (opcional)
            
        Returns:
            bool: True si se cargó exitosamente, False en caso contrario
        """
        try:
            logger.info(f"🔄 Precargando DataFrame desde: {excel_path}")
            logger.info(f"   Cliente: {self.client_config.client_name}")
            
            persistent_cache.load_dataframe(excel_path, sheet_name)
            
            # Inyectar DataFrame en el sandbox para que esté disponible
            df = persistent_cache.get_dataframe()
            if df is not None:
                self.sandbox.inject_dataframe(df)
                logger.info("✅ DataFrame precargado e inyectado en sandbox exitosamente")
            
            return True
        except Exception as e:
            logger.error(f"❌ Error precargando DataFrame: {e}")
            return False
    
    def is_dataframe_ready(self) -> bool:
        """Verifica si el DataFrame está listo para usar."""
        return persistent_cache.is_loaded()
    
    def _build_system_prompt(self) -> str:
        """
        Construye el prompt del sistema personalizado para el cliente.
        
        Returns:
            str: Prompt del sistema
        """
        base_prompt = """Eres un experto en pandas que genera código Python para analizar datos Excel.

REGLAS CRÍTICAS:
1. El DataFrame YA ESTÁ CARGADO en la variable 'df' - NO lo cargues
2. Genera código Python válido y ejecutable
3. NO uses markdown (```python) - solo código plano
4. USA SIEMPRE 4 ESPACIOS para indentación, nunca tabs
5. Cada línea debe empezar sin espacios extra al inicio

CÓDIGO SEGURO Y CONSISTENTE:
- Para filtrar NaN: df_clean = df.dropna(subset=['columna']).copy()
- Para contar: df['columna'].value_counts()
- Para máximos: .idxmax() y .max()
- Convierte a string cuando sea necesario: .astype(str)
- USA print() para mostrar resultados finales
- Para caracteres especiales usa: print(f"Texto: {variable}")
- Evita usar comillas simples en strings con acentos

EJEMPLO DE FORMATO CORRECTO:
df_clean = df.dropna(subset=['numbercall']).copy()
counts = df_clean['numbercall'].value_counts()
print(f"Resultado: {counts.idxmax()}")"""

        # Añadir contexto específico del cliente
        specialized_context = self.client_config.get_specialized_prompt_context()
        if specialized_context:
            base_prompt += f"\n\nCONTEXTO ESPECÍFICO DEL DOMINIO:\n{specialized_context}"
        
        return base_prompt
    
    def generate_code(self, prompt: str) -> str:
        """
        Genera código Python usando el API de Groq con prompts personalizados.
        
        Args:
            prompt: Prompt para generación de código
            
        Returns:
            str: Código Python generado
            
        Raises:
            PromptError: Si falla la generación
        """
        try:
            logger.debug(f"🤖 Generando código con Groq para cliente: {self.client_config.client_name}")
            
            system_prompt = self._build_system_prompt()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                stream=False
            )
            
            content = response.choices[0].message.content or ""
            code = content.strip()
            
            # Limpiar código 
            if code.startswith("```python"):
                code = code.replace("```python", "").replace("```", "").strip()
            elif code.startswith("```"):
                code = code.replace("```", "").strip()
            
            # Limpiar líneas vacías al inicio y final
            lines = code.split('\n')
            lines = [line for line in lines if line.strip()]  # Eliminar líneas vacías
            
            # Normalizar indentación (convertir tabs a espacios)
            normalized_lines = []
            for line in lines:
                # Convertir tabs a 4 espacios
                line = line.expandtabs(4)
                normalized_lines.append(line)
            
            code = '\n'.join(normalized_lines)
            
            logger.debug(f"✅ Código generado y limpiado: {len(code)} caracteres")
            return code
            
        except Exception as e:
            logger.error(f"❌ Error generando código: {e}")
            raise PromptError(f"Error al generar código: {e}")
    
    def build_prompt(self, question: str) -> str:
        """
        Construye el prompt para Groq usando solo esquema y ejemplos.
        
        Args:
            question: Pregunta del usuario
            
        Returns:
            str: Prompt construido
        """
        # Obtener resumen del esquema (sin datos completos)
        schema_summary = persistent_cache.get_schema_summary()
        
        if not schema_summary:
            raise ValueError("No hay DataFrame cargado en caché")
        
        # Construir prompt con información estructural únicamente
        prompt = f"""
INFORMACIÓN DEL DATASET:
- Cliente: {self.client_config.client_name}
- Archivo: {schema_summary.get('file_path', 'No especificado')}
- Filas: {schema_summary.get('rows', 0):,}
- Columnas: {schema_summary.get('columns', 0)}

COLUMNAS DISPONIBLES:
{', '.join(schema_summary.get('column_names', []))}

TIPOS DE DATOS:
{chr(10).join(f"- {col}: {dtype}" for col, dtype in schema_summary.get('dtypes', {}).items())}

EJEMPLO DE DATOS (primeras filas):
{schema_summary.get('sample_data', [])}

PREGUNTA DEL USUARIO:
{question}

INSTRUCCIONES:
- El DataFrame YA ESTÁ CARGADO en la variable 'df' - NO lo cargues nuevamente
- Genera **solo** el código Python usando pandas para obtener la respuesta
- Devuelve únicamente el bloque de código, sin explicaciones
- Asegúrate de que el código sea ejecutable y produzca un resultado claro
- Si trabajas con fechas, convierte primero con pd.to_datetime() antes de usar .dt
- Para análisis de agrupación, usa .reset_index() cuando sea necesario
- Maneja valores NaN apropiadamente con .dropna() o .fillna()
- Al filtrar datos, usa df_filtrado = df[condicion].copy() para evitar warnings
- Usa print() para mostrar resultados importantes y claros
"""
        
        return prompt
    
    def ask(self, excel_path: str, question: str, sheet_name: Optional[str] = None) -> Any:
        """
        Procesa una pregunta sobre el Excel.
        
        Args:
            excel_path: Ruta al archivo Excel
            question: Pregunta del usuario
            sheet_name: Nombre de la hoja (opcional)
            
        Returns:
            Any: Resultado del análisis
            
        Raises:
            ValueError: Si no se puede cargar el DataFrame
            ExecutionError: Si falla la ejecución del código
        """
        try:
            # Verificar si necesita precargar el DataFrame
            current_file = persistent_cache.get_current_file()
            if current_file != excel_path:
                logger.info("🔄 Necesita cargar nuevo DataFrame")
                if not self.preload_dataframe(excel_path, sheet_name):
                    raise ValueError("No se pudo cargar el DataFrame")
            
            # Verificar que el DataFrame está listo
            if not self.is_dataframe_ready():
                raise ValueError("DataFrame no está disponible en caché")
            
            # Construir prompt (solo con esquema, no datos completos)
            prompt = self.build_prompt(question)
            
            # Generar código
            code = self.generate_code(prompt)
            
            # Ejecutar código directamente (el DataFrame ya está inyectado en el sandbox)
            logger.debug("🔄 Ejecutando código en sandbox con DataFrame pre-inyectado...")
            stdout, stderr = self.sandbox.execute_code(code)
            
            if stderr:
                logger.error(f"❌ Error en sandbox: {stderr}")
                raise ExecutionError(stderr)
            
            # Parsear resultado
            result = parse_output(stdout)
            logger.info("✅ Consulta procesada exitosamente")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error procesando consulta: {e}")
            raise
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché."""
        return persistent_cache.get_stats()
    
    def clear_cache(self):
        """Limpia el caché y el DataFrame inyectado."""
        persistent_cache.clear_cache()
        self.sandbox.clear_injected_dataframe()
        logger.info("🧹 Caché y DataFrame inyectado limpiados")
    
    def update_client_config(self, new_client_config: ClientConfig):
        """
        Actualiza la configuración del cliente.
        
        Args:
            new_client_config: Nueva configuración de cliente
        """
        self.client_config = new_client_config
        logger.info(f"🔄 Configuración actualizada para cliente: {new_client_config.client_name}")

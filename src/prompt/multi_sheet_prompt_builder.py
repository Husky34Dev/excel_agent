"""
Construye prompts inteligentes para consultas en archivos Excel con múltiples hojas.
"""
from typing import Dict, List, Optional
from src.loader.excel_loader import SheetInfo, ColumnSchema

def build_multi_sheet_prompt(all_sheets: Dict[str, SheetInfo], question: str, excel_path: Optional[str] = None) -> str:
    """
    Construye un prompt para consultas que pueden abarcar múltiples hojas.
    
    Args:
        all_sheets: Diccionario con información de todas las hojas cargadas
        question: Pregunta del usuario
        excel_path: Ruta real del archivo Excel
        
    Returns:
        str: Prompt completo para el modelo
    """
    # Usar ruta real si está disponible, sino usar placeholder
    file_path = f"'{excel_path}'" if excel_path else "'EXCEL_PATH'"
    
    # Introducción sobre las hojas disponibles
    sheets_overview = "Tienes acceso a un archivo Excel con múltiples hojas:\n\n"
    
    for sheet_name, sheet_info in all_sheets.items():
        sheets_overview += f"**HOJA: '{sheet_name}'** ({sheet_info['rows']} filas × {sheet_info['columns']} columnas)\n"
        
        # Mostrar esquema de columnas
        for col_schema in sheet_info['schema']:
            samples = ', '.join(col_schema['sample_values'][:3])
            sheets_overview += f"  • {col_schema['name']} ({col_schema['dtype']}): ejemplos: {samples}\n"
        sheets_overview += "\n"
    
    # Instrucciones para trabajar con múltiples hojas
    multi_sheet_instructions = f"""
INSTRUCCIONES PARA MÚLTIPLES HOJAS:

1. **Carga de datos**: Para cada hoja usa:
   ```python
   # Para la hoja 'Ventas':
   df_ventas = pd.read_excel({file_path}, sheet_name='Ventas')
   
   # Para la hoja 'Clientes':
   df_clientes = pd.read_excel({file_path}, sheet_name='Clientes')
   ```

2. **Análisis inteligente**:
   - Analiza qué hoja(s) necesitas según la pregunta
   - Si la pregunta requiere datos de múltiples hojas, úsalas
   - Si es específica a una hoja, usa solo esa

3. **Relaciones entre hojas**:
   - Busca columnas comunes para hacer JOIN (id_cliente, id_producto, etc.)
   - Usa pd.merge() para combinar datos de diferentes hojas
   - Ejemplo: `df_resultado = pd.merge(df_ventas, df_clientes, on='id_cliente')`

4. **Variables de DataFrame**:
   - Usa nombres descriptivos: df_ventas, df_clientes, df_productos, etc.
   - No uses 'df' genérico cuando hay múltiples hojas

5. **Optimización**:
   - Solo carga las hojas que realmente necesites para responder la pregunta
   - Si la pregunta es específica a una hoja, no cargues las demás

"""
    
    # Prompt principal
    main_prompt = f"""
{sheets_overview}

{multi_sheet_instructions}

**PREGUNTA DEL USUARIO:**
{question}

**TU TAREA:**
1. Determina qué hoja(s) necesitas para responder la pregunta
2. Genera código Python que:
   - Cargue solo las hojas necesarias con pd.read_excel({file_path}, sheet_name='nombre_hoja')
   - Realice el análisis requerido
   - Combine datos de múltiples hojas si es necesario (usando merge, join, etc.)
   - Produzca una respuesta clara y directa

**IMPORTANTE:**
- SIEMPRE usa la ruta exacta: {file_path}
- Asegúrate de que el código sea ejecutable y produzca un resultado claro
- No incluyas explicaciones, solo el código Python
- Usa nombres descriptivos para los DataFrames (df_ventas, df_clientes, etc.)
- Convierte fechas con pd.to_datetime() cuando sea necesario
- Para análisis que requieran múltiples hojas, combínalas inteligentemente
- Importa pandas como pd al inicio del código

Genera **únicamente** el código Python:
"""
    
    return main_prompt

def build_single_sheet_prompt(schema: List[ColumnSchema], question: str, excel_path: Optional[str] = None) -> str:
    """
    Construye un prompt para consultas de una sola hoja (compatibilidad).
    
    Args:
        schema: Esquema de la hoja
        question: Pregunta del usuario
        excel_path: Ruta real del archivo Excel
        
    Returns:
        str: Prompt para el modelo
    """
    # Usar ruta real si está disponible, sino usar placeholder
    file_path = f"'{excel_path}'" if excel_path else "'EXCEL_PATH'"
    
    # Construir descripción del esquema
    schema_description = "Tienes un DataFrame llamado 'df' con las siguientes columnas:\n"
    
    for col in schema:
        samples = ', '.join(col['sample_values'][:5])
        schema_description += f"- {col['name']} (tipo: {col['dtype']}), ejemplos: {samples}\n"
    
    prompt = f"""{schema_description}

Con base en este esquema, responde a:
{question}

Instrucciones:
- Genera **solo** el código Python usando pandas para obtener la respuesta
- Usa el DataFrame 'df' como variable principal, asegurándote de que esté definido como:
  df = pd.read_excel({file_path})
- Devuelve únicamente el bloque de código, sin explicaciones
- Asegúrate de que el código sea ejecutable y produzca un resultado claro

Mejores prácticas para evitar errores:
- Usa .copy() al crear subconjuntos del DataFrame para evitar SettingWithCopyWarning
- Usa .loc[] para asignaciones seguras de columnas
- SIEMPRE convierte fechas con pd.to_datetime() antes de usar .dt accessor: df['fecha'] = pd.to_datetime(df['fecha'])
- Para operaciones de agrupación, usa .reset_index() cuando sea necesario
- Maneja valores NaN con .dropna() o .fillna() antes de usar .idxmax()/.idxmin()
- Al filtrar datos, usa df_filtrado = df[condicion].copy()
- Para análisis temporal, primero convierte fechas y luego extrae componentes: año, trimestre, mes
- Usa df['fecha'].dt.quarter para obtener trimestres, df['fecha'].dt.year para años
- Importa pandas como pd al inicio del código
"""
    
    return prompt

def build_prompt(schema_or_sheets, question: str, excel_path: Optional[str] = None) -> str:
    """
    Función principal que decide qué tipo de prompt construir.
    
    Args:
        schema_or_sheets: Lista de ColumnSchema (una hoja) o Dict de SheetInfo (múltiples hojas)
        question: Pregunta del usuario
        excel_path: Ruta real del archivo Excel
        
    Returns:
        str: Prompt apropiado
    """
    if isinstance(schema_or_sheets, dict):
        # Es un diccionario de múltiples hojas
        return build_multi_sheet_prompt(schema_or_sheets, question, excel_path)
    else:
        # Es una lista de ColumnSchema (una sola hoja)
        return build_single_sheet_prompt(schema_or_sheets, question, excel_path)

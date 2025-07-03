from typing import List
from src.loader.excel_loader import ColumnSchema

def build_prompt(
    schema: List[ColumnSchema],
    question: str,
    table_name: str = "df",
    file_path: str = "data/input/demo.xlsx"
) -> str:
    """
    Construye el prompt para el agente, incluyendo esquema y pregunta.
    
    Args:
        schema: Lista de esquemas de columnas del DataFrame
        question: Pregunta del usuario sobre los datos
        table_name: Nombre de referencia para el DataFrame (default: "df")
        file_path: Ruta al archivo Excel (default: "data/input/demo.xlsx")
        
    Returns:
        str: Prompt formateado para el modelo LLM
        
    Example:
        >>> schema = [{"name": "ventas", "dtype": "int64", "sample_values": ["100", "200"]}]
        >>> prompt = build_prompt(schema, "¿Cuál es el promedio de ventas?", file_path="data/input/demo.xlsx")
        >>> print(prompt)
    """
    # Validaciones básicas
    if not schema:
        raise ValueError("El esquema no puede estar vacío")
    if not question.strip():
        raise ValueError("La pregunta no puede estar vacía")
    
    # Construir descripción del esquema
    schema_lines = [f"Tienes un DataFrame llamado '{table_name}' con las siguientes columnas:"]
    
    for col in schema:
        samples = ", ".join(col["sample_values"]) if col["sample_values"] else "sin muestras"
        schema_lines.append(f"- {col['name']} (tipo: {col['dtype']}), ejemplos: {samples}")
    
    # Template del prompt
    prompt_template = f"""
{chr(10).join(schema_lines)}

Con base en este esquema, responde a:
{question}

Instrucciones:
- Genera **solo** el código Python usando pandas para obtener la respuesta
- Usa el DataFrame '{table_name}' como variable principal, asegurándote de que esté definido como:
  df = pd.read_excel('{file_path}')
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
""".strip()
    
    return prompt_template

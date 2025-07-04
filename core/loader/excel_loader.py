import pandas as pd
from typing import List, TypedDict, Union, Dict
from pathlib import Path
from config.settings import get_settings
from config.logger_config import get_logger
from .multi_sheet_handler import MultiSheetHandler

logger = get_logger(__name__)

class ColumnSchema(TypedDict):
    """Esquema de una columna del DataFrame."""
    name: str
    dtype: str
    sample_values: List[str]

class SheetInfo(TypedDict):
    """Información completa de una hoja."""
    name: str
    dataframe: pd.DataFrame
    schema: List[ColumnSchema]
    rows: int
    columns: int

def load_all_sheets(path: str) -> Dict[str, SheetInfo]:
    """
    Carga TODAS las hojas de un archivo Excel.
    
    Args:
        path: Ruta al archivo Excel
        
    Returns:
        Dict[str, SheetInfo]: Diccionario con información de todas las hojas
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si hay problemas al leer el archivo Excel
    """
    # Verificar que el archivo existe
    excel_path = Path(path)
    if not excel_path.exists():
        raise FileNotFoundError(f"Archivo Excel no encontrado: {path}")
    
    try:
        logger.info(f"Cargando TODAS las hojas del Excel: {path}")
        
        # Obtener información de todas las hojas
        handler = MultiSheetHandler(path)
        sheets_info = handler.get_sheets_info()
        
        all_sheets = {}
        loaded_sheets = 0
        
        for sheet_name, info in sheets_info.items():
            # Solo cargar hojas que no estén vacías y no tengan errores
            if not info.get('is_empty', True) and not info.get('error'):
                try:
                    logger.debug(f"Cargando hoja: {sheet_name}")
                    df = pd.read_excel(path, sheet_name=sheet_name)
                    
                    if not df.empty:
                        schema = infer_schema(df)
                        
                        all_sheets[sheet_name] = {
                            'name': sheet_name,
                            'dataframe': df,
                            'schema': schema,
                            'rows': len(df),
                            'columns': len(df.columns)
                        }
                        loaded_sheets += 1
                        logger.debug(f"Hoja '{sheet_name}' cargada: {len(df)} filas × {len(df.columns)} columnas")
                    else:
                        logger.warning(f"Hoja '{sheet_name}' está vacía, omitiendo")
                        
                except Exception as e:
                    logger.warning(f"Error cargando hoja '{sheet_name}': {e}")
                    continue
            else:
                logger.debug(f"Omitiendo hoja '{sheet_name}': vacía o con errores")
        
        if not all_sheets:
            raise ValueError("No se pudieron cargar hojas válidas del archivo Excel")
        
        logger.info(f"Cargadas {loaded_sheets} hojas exitosamente")
        return all_sheets
        
    except Exception as e:
        error_msg = f"Error al cargar todas las hojas del Excel {path}: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e

def load_excel(
    path: str, 
    sheet_name: Union[str, int, None] = None,
    auto_detect_best_sheet: bool = True
) -> pd.DataFrame:
    """
    Carga un archivo Excel y devuelve un DataFrame de UNA hoja específica.
    
    NOTA: Esta función se mantiene para compatibilidad, pero se recomienda usar load_all_sheets()
    
    Args:
        path: Ruta al archivo Excel
        sheet_name: Nombre o índice de la hoja. Si es None, usa auto-detección o configuración default
        auto_detect_best_sheet: Si True, detecta automáticamente la mejor hoja en archivos multi-hoja
        
    Returns:
        pd.DataFrame: DataFrame cargado
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si hay problemas al leer el archivo Excel
    """
    # Verificar que el archivo existe
    excel_path = Path(path)
    if not excel_path.exists():
        raise FileNotFoundError(f"Archivo Excel no encontrado: {path}")
    
    try:
        # Si no se especifica hoja, usar auto-detección o configuración
        if sheet_name is None:
            handler = MultiSheetHandler(path)
            
            if handler.has_multiple_sheets() and auto_detect_best_sheet:
                suggested_sheet, reason = handler.suggest_best_sheet()
                logger.info(f"Archivo multi-hoja detectado. Usando hoja sugerida: '{suggested_sheet}' ({reason})")
                sheet_name = suggested_sheet
                
                # Mostrar resumen si hay múltiples hojas
                print(f"📊 Detectadas múltiples hojas en {excel_path.name}")
                print(f"💡 Usando automáticamente: '{suggested_sheet}' - {reason}")
                print("⚙️  Para usar otra hoja específica, usa: --sheet 'nombre_hoja'")
            else:
                # Usar configuración default
                settings = get_settings()
                sheet_name = int(settings.excel_default_sheet) if settings.excel_default_sheet.isdigit() else settings.excel_default_sheet
        
        logger.info(f"Cargando Excel: {path}, hoja: {sheet_name}")
        df = pd.read_excel(path, sheet_name=sheet_name)
        logger.debug(f"Excel cargado exitosamente. Shape: {df.shape}")
        
        if df.empty:
            raise ValueError(f"La hoja '{sheet_name}' está vacía o no contiene datos válidos")
        
        return df
        
    except Exception as e:
        error_msg = f"Error al cargar Excel {path}: {str(e)}"
        logger.error(error_msg)
        raise ValueError(error_msg) from e

def get_excel_sheets_info(path: str) -> dict:
    """
    Obtiene información sobre todas las hojas de un archivo Excel.
    
    Args:
        path: Ruta al archivo Excel
        
    Returns:
        Dict con información de cada hoja
    """
    handler = MultiSheetHandler(path)
    return handler.get_sheets_info()

def infer_schema(df: pd.DataFrame, num_samples: int = 5) -> List[ColumnSchema]:
    """
    Infiere nombre, tipo y muestras de cada columna del DataFrame.
    
    Args:
        df: DataFrame de pandas
        num_samples: Número máximo de valores de muestra por columna
        
    Returns:
        List[ColumnSchema]: Lista con el esquema de cada columna
        
    Example:
        >>> df = pd.DataFrame({"ventas": [100, 200], "region": ["Norte", "Sur"]})
        >>> schema = infer_schema(df)
        >>> print(schema[0]["name"])  # "ventas"
    """
    if df.empty:
        logger.warning("DataFrame vacío, retornando esquema vacío")
        return []
    
    schema: List[ColumnSchema] = []
    logger.debug(f"Infiriendo esquema para {len(df.columns)} columnas")
    
    for col in df.columns:
        # Obtener tipo de dato
        dtype = str(df[col].dtype)
        
        # Obtener valores de muestra únicos (sin NaN)
        samples = (
            df[col]
            .dropna()
            .astype(str)
            .unique()
            .tolist()[:num_samples]
        )
        
        schema.append({
            "name": str(col),  # Asegurar que sea string
            "dtype": dtype,
            "sample_values": samples
        })
        
        logger.debug(f"Columna '{col}': tipo={dtype}, muestras={len(samples)}")
    
    logger.info(f"Esquema inferido para {len(schema)} columnas")
    return schema

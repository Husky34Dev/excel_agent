"""
Manejador para archivos Excel con múltiples hojas.
"""
import pandas as pd
from typing import Dict, List, Tuple, Union
from pathlib import Path
from config.logger_config import get_logger

logger = get_logger(__name__)

class MultiSheetHandler:
    """Manejador para archivos Excel con múltiples hojas."""
    
    def __init__(self, excel_path: str):
        """
        Inicializa el manejador con un archivo Excel.
        
        Args:
            excel_path: Ruta al archivo Excel
        """
        self.excel_path = Path(excel_path)
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Archivo Excel no encontrado: {excel_path}")
        
        self._sheets_info = None
    
    def get_sheets_info(self) -> Dict[str, Dict]:
        """
        Obtiene información sobre todas las hojas del archivo Excel.
        
        Returns:
            Dict con información de cada hoja: nombre, filas, columnas, primeras columnas
        """
        if self._sheets_info is not None:
            return self._sheets_info
        
        try:
            logger.info(f"Analizando hojas del archivo: {self.excel_path}")
            
            # Obtener nombres de todas las hojas
            excel_file = pd.ExcelFile(self.excel_path)
            sheet_names = excel_file.sheet_names
            
            sheets_info = {}
            
            for sheet_name in sheet_names:
                try:
                    # Leer solo las primeras filas para obtener info básica
                    df_sample = pd.read_excel(self.excel_path, sheet_name=sheet_name, nrows=5)
                    
                    # Leer toda la hoja para obtener el conteo real de filas
                    df_full = pd.read_excel(self.excel_path, sheet_name=sheet_name)
                    
                    sheets_info[sheet_name] = {
                        'rows': len(df_full),
                        'columns': len(df_full.columns),
                        'column_names': df_full.columns.tolist(),
                        'sample_data': df_sample.head(3).to_dict('records') if not df_sample.empty else [],
                        'is_empty': df_full.empty
                    }
                    
                    logger.debug(f"Hoja '{sheet_name}': {len(df_full)} filas, {len(df_full.columns)} columnas")
                    
                except Exception as e:
                    logger.warning(f"Error leyendo hoja '{sheet_name}': {e}")
                    sheets_info[sheet_name] = {
                        'rows': 0,
                        'columns': 0,
                        'column_names': [],
                        'sample_data': [],
                        'is_empty': True,
                        'error': str(e)
                    }
            
            self._sheets_info = sheets_info
            logger.info(f"Análisis completado: {len(sheets_info)} hojas encontradas")
            return sheets_info
            
        except Exception as e:
            logger.error(f"Error analizando archivo Excel: {e}")
            raise ValueError(f"Error al analizar el archivo Excel: {e}")
    
    def has_multiple_sheets(self) -> bool:
        """Verifica si el archivo tiene múltiples hojas."""
        sheets_info = self.get_sheets_info()
        return len(sheets_info) > 1
    
    def get_largest_sheet(self) -> str:
        """
        Obtiene el nombre de la hoja con más datos (filas * columnas).
        
        Returns:
            Nombre de la hoja más grande
        """
        sheets_info = self.get_sheets_info()
        
        if not sheets_info:
            raise ValueError("No se encontraron hojas válidas en el archivo")
        
        # Calcular tamaño (filas * columnas) para cada hoja no vacía
        sheet_sizes = {}
        for name, info in sheets_info.items():
            if not info.get('is_empty', True) and not info.get('error'):
                sheet_sizes[name] = info['rows'] * info['columns']
        
        if not sheet_sizes:
            # Si todas están vacías, devolver la primera
            return list(sheets_info.keys())[0]
        
        largest_sheet = max(sheet_sizes.items(), key=lambda x: x[1])[0]
        logger.info(f"Hoja más grande identificada: '{largest_sheet}' ({sheet_sizes[largest_sheet]} celdas)")
        return largest_sheet
    
    def suggest_best_sheet(self) -> Tuple[str, str]:
        """
        Sugiere la mejor hoja para análisis basada en heurísticas.
        
        Returns:
            Tuple con (nombre_hoja, razón_sugerencia)
        """
        sheets_info = self.get_sheets_info()
        
        # Filtrar hojas vacías o con errores
        valid_sheets = {
            name: info for name, info in sheets_info.items() 
            if not info.get('is_empty', True) and not info.get('error')
        }
        
        if not valid_sheets:
            first_sheet = list(sheets_info.keys())[0]
            return first_sheet, "Primera hoja (no se encontraron hojas con datos válidos)"
        
        # Heurísticas para seleccionar la mejor hoja:
        
        # 1. Buscar hojas con nombres que sugieran datos principales
        priority_names = ['datos', 'data', 'main', 'principal', 'hoja1', 'sheet1']
        for name in valid_sheets:
            if name.lower() in priority_names:
                return name, f"Hoja con nombre prioritario: '{name}'"
        
        # 2. Buscar la hoja con más filas (más datos)
        sheet_with_most_rows = max(valid_sheets.items(), key=lambda x: x[1]['rows'])
        most_rows_name = sheet_with_most_rows[0]
        most_rows_count = sheet_with_most_rows[1]['rows']
        
        # 3. Buscar la hoja con más columnas (más rica en datos)
        sheet_with_most_cols = max(valid_sheets.items(), key=lambda x: x[1]['columns'])
        most_cols_name = sheet_with_most_cols[0]
        most_cols_count = sheet_with_most_cols[1]['columns']
        
        # Si una hoja tiene significativamente más filas, preferirla
        if most_rows_count > 50:  # Umbral mínimo de filas para considerar datos sustanciales
            return most_rows_name, f"Hoja con más datos ({most_rows_count} filas)"
        
        # Si las filas son similares, preferir la que tenga más columnas
        return most_cols_name, f"Hoja con más variedad de datos ({most_cols_count} columnas)"
    
    def print_sheets_summary(self) -> None:
        """Imprime un resumen de todas las hojas encontradas."""
        sheets_info = self.get_sheets_info()
        
        print(f"\n📊 ANÁLISIS DEL ARCHIVO EXCEL: {self.excel_path.name}")
        print("=" * 60)
        print(f"🔢 Total de hojas encontradas: {len(sheets_info)}")
        
        if len(sheets_info) > 1:
            print("⚠️  ARCHIVO CON MÚLTIPLES HOJAS DETECTADO")
        
        print("\n📋 DETALLES POR HOJA:")
        print("-" * 60)
        
        for i, (name, info) in enumerate(sheets_info.items(), 1):
            status = "❌ Vacía/Error" if info.get('is_empty', True) or info.get('error') else "✅ Con datos"
            
            print(f"{i}. Hoja: '{name}' {status}")
            
            if info.get('error'):
                print(f"   Error: {info['error']}")
            elif not info.get('is_empty', True):
                print(f"   📏 Dimensiones: {info['rows']} filas × {info['columns']} columnas")
                print(f"   📑 Columnas: {', '.join(info['column_names'][:5])}")
                if len(info['column_names']) > 5:
                    print(f"   ... y {len(info['column_names']) - 5} más")
        
        if len(sheets_info) > 1:
            suggested_sheet, reason = self.suggest_best_sheet()
            print(f"\n💡 HOJA RECOMENDADA: '{suggested_sheet}'")
            print(f"   Razón: {reason}")
            print(f"\n⚙️  Para usar otra hoja, especifica: --sheet 'nombre_hoja'")
        
        print("-" * 60)


def analyze_excel_file(excel_path: str) -> MultiSheetHandler:
    """
    Función helper para analizar rápidamente un archivo Excel.
    
    Args:
        excel_path: Ruta al archivo Excel
        
    Returns:
        MultiSheetHandler configurado
    """
    handler = MultiSheetHandler(excel_path)
    handler.print_sheets_summary()
    return handler

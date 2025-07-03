import sys
import pandas as pd
from pathlib import Path

def csv_to_xlsx(csv_path: str, xlsx_path: str):
    """Convierte un archivo CSV a Excel (XLSX)"""
    try:
        print(f"📄 Leyendo CSV: {csv_path}")
        
        # Verificar que el archivo CSV existe
        if not Path(csv_path).exists():
            print(f"❌ Error: Archivo CSV no encontrado: {csv_path}")
            return False
        
        # Leer el CSV con diferentes encodings por si hay problemas
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(csv_path, encoding='latin1')
                print("⚠️  Usando encoding latin1")
            except UnicodeDecodeError:
                df = pd.read_csv(csv_path, encoding='cp1252')
                print("⚠️  Usando encoding cp1252")
        
        print(f"📊 Datos leídos: {len(df)} filas, {len(df.columns)} columnas")
        print(f"📈 Columnas: {list(df.columns)}")
        
        # Crear directorio de salida si no existe
        output_path = Path(xlsx_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Escribir al XLSX
        df.to_excel(xlsx_path, index=False, engine='openpyxl')
        print(f"✅ Convertido exitosamente: '{csv_path}' → '{xlsx_path}'")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la conversión: {str(e)}")
        return False

def main():
    # Configuración específica para casino.csv → casino.xlsx
    csv_path = "casino.csv"
    xlsx_path = "casino.xlsx"
    
    # Si se proporcionan argumentos de línea de comandos, usarlos
    if len(sys.argv) == 3:
        csv_path = sys.argv[1]
        xlsx_path = sys.argv[2]
    elif len(sys.argv) == 2:
        csv_path = sys.argv[1]
        # Generar nombre de salida automáticamente
        xlsx_path = Path(csv_path).stem + ".xlsx"
    
    print("🔄 CONVERSOR CSV → XLSX")
    print("=" * 40)
    
    success = csv_to_xlsx(csv_path, xlsx_path)
    
    if success:
        print("\n🎉 Conversión completada!")
        print(f"📁 Archivo generado: {xlsx_path}")
    else:
        print("\n💥 La conversión falló")
        sys.exit(1)

if __name__ == "__main__":
    main()
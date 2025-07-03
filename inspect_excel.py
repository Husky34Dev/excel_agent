import pandas as pd

def inspect_excel():
    """Inspecciona el archivo Excel de demostración mostrando estructura y estadísticas básicas."""
    file_path = 'data/input/demo.xlsx'
    try:
        df = pd.read_excel(file_path)
        print(f"📊 INSPECCIÓN DEL ARCHIVO: {file_path}")
        print("=" * 50)
        print(f"📋 Columnas: {df.columns.tolist()}")
        print(f"📈 Número de registros: {len(df)}")
        print(f"🗓️  Rango de fechas: {df['fecha'].min()} a {df['fecha'].max()}")
        print(f"🌍 Regiones: {df['región'].unique()}")
        print("\n📋 Primeras 5 filas:")
        print(df.head())
        print("\n📊 Estadísticas básicas:")
        print(df.describe())
    except Exception as e:
        print(f"❌ Error inspeccionando archivo Excel: {e}")

if __name__ == "__main__":
    inspect_excel()

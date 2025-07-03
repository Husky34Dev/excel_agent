"""
Script para calcular respuestas esperadas de consultas complejas sobre demo.xlsx
"""
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta

def load_data():
    """Cargar datos del Excel demo"""
    excel_path = Path("../data/input/demo.xlsx")
    df = pd.read_excel(excel_path)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['beneficio'] = df['ingresos'] - df['gastos']
    df['margen'] = (df['beneficio'] / df['ingresos']) * 100
    return df

def calculate_complex_queries(df):
    """Calcular respuestas para consultas complejas"""
    results = {}
    
    # 1. Región con mayor beneficio total
    beneficio_por_region = df.groupby('región')['beneficio'].sum()
    results['region_mayor_beneficio'] = {
        'query': '¿Cuál es la región con mayor beneficio total?',
        'expected': beneficio_por_region.idxmax(),
        'value': float(beneficio_por_region.max())
    }
    
    # 2. Promedio de margen de beneficio por región
    margen_promedio_region = df.groupby('región')['margen'].mean()
    results['margen_promedio_por_region'] = {
        'query': '¿Cuál es el promedio de margen de beneficio por región?',
        'expected': margen_promedio_region.to_dict(),
        'overall_avg': float(margen_promedio_region.mean())
    }
    
    # 3. Mes con mayores ingresos totales
    df['mes_año'] = df['fecha'].dt.to_period('M')
    ingresos_por_mes = df.groupby('mes_año')['ingresos'].sum()
    mes_max_ingresos = ingresos_por_mes.idxmax()
    results['mes_mayores_ingresos'] = {
        'query': '¿En qué mes se registraron los mayores ingresos totales?',
        'expected': str(mes_max_ingresos),
        'value': float(ingresos_por_mes.max())
    }
    
    # 4. Correlación entre ingresos y gastos
    correlacion = df['ingresos'].corr(df['gastos'])
    results['correlacion_ingresos_gastos'] = {
        'query': '¿Cuál es la correlación entre ingresos y gastos?',
        'expected': float(correlacion),
        'interpretation': 'Positiva fuerte' if correlacion > 0.7 else 'Positiva moderada' if correlacion > 0.3 else 'Débil'
    }
    
    # 5. Región más eficiente (menor ratio gastos/ingresos)
    df['ratio_eficiencia'] = df['gastos'] / df['ingresos']
    eficiencia_por_region = df.groupby('región')['ratio_eficiencia'].mean()
    region_mas_eficiente = eficiencia_por_region.idxmin()
    results['region_mas_eficiente'] = {
        'query': '¿Cuál es la región más eficiente (menor ratio gastos/ingresos)?',
        'expected': region_mas_eficiente,
        'ratio': float(eficiencia_por_region.min())
    }
    
    # 6. Tendencia temporal de beneficios
    df_temporal = df.set_index('fecha').resample('M')['beneficio'].mean()
    tendencia = np.polyfit(range(len(df_temporal)), df_temporal.values, 1)[0]
    results['tendencia_beneficios'] = {
        'query': '¿Cuál es la tendencia temporal de los beneficios mensuales?',
        'expected': 'Creciente' if tendencia > 0 else 'Decreciente',
        'slope': float(tendencia)
    }
    
    # 7. Outliers en ingresos (valores atípicos)
    Q1 = df['ingresos'].quantile(0.25)
    Q3 = df['ingresos'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df['ingresos'] < lower_bound) | (df['ingresos'] > upper_bound)]
    results['outliers_ingresos'] = {
        'query': '¿Cuántos valores atípicos hay en los ingresos y cuáles son?',
        'expected': len(outliers),
        'outliers': outliers[['región', 'ingresos', 'fecha']].to_dict('records')
    }
    
    # 8. Mejor trimestre por beneficios
    df['trimestre'] = df['fecha'].dt.quarter
    df['año'] = df['fecha'].dt.year
    df['año_trimestre'] = df['año'].astype(str) + '-Q' + df['trimestre'].astype(str)
    beneficio_trimestre = df.groupby('año_trimestre')['beneficio'].sum()
    mejor_trimestre = beneficio_trimestre.idxmax()
    results['mejor_trimestre'] = {
        'query': '¿Cuál fue el trimestre con mejores beneficios totales?',
        'expected': mejor_trimestre,
        'value': float(beneficio_trimestre.max())
    }
    
    # 9. Distribución de registros por región
    distribucion_region = df['región'].value_counts()
    results['distribucion_por_region'] = {
        'query': '¿Cómo se distribuyen los registros por región?',
        'expected': distribucion_region.to_dict(),
        'region_mas_registros': distribucion_region.idxmax(),
        'max_registros': int(distribucion_region.max())
    }
    
    # 10. Rango de fechas y días transcurridos
    fecha_min = df['fecha'].min()
    fecha_max = df['fecha'].max()
    dias_transcurridos = (fecha_max - fecha_min).days
    results['rango_temporal'] = {
        'query': '¿Cuál es el rango temporal de los datos y cuántos días abarca?',
        'fecha_inicio': fecha_min.strftime('%Y-%m-%d'),
        'fecha_fin': fecha_max.strftime('%Y-%m-%d'),
        'dias_totales': dias_transcurridos
    }
    
    return results

def save_results(results):
    """Guardar resultados en JSON"""
    output_path = Path("expected_results.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"✅ Resultados guardados en: {output_path}")

def print_summary(results):
    """Imprimir resumen de resultados"""
    print("\n" + "="*80)
    print("📊 RESUMEN DE CONSULTAS COMPLEJAS Y RESPUESTAS ESPERADAS")
    print("="*80)
    
    for i, (key, data) in enumerate(results.items(), 1):
        print(f"\n{i}. {data['query']}")
        print("-" * len(data['query']))
        
        if 'expected' in data:
            if isinstance(data['expected'], dict):
                print("Respuesta esperada:")
                for k, v in data['expected'].items():
                    print(f"  • {k}: {v:.2f}" if isinstance(v, float) else f"  • {k}: {v}")
            else:
                print(f"Respuesta esperada: {data['expected']}")
        
        if 'value' in data:
            print(f"Valor: {data['value']:,.2f}")
        
        if 'interpretation' in data:
            print(f"Interpretación: {data['interpretation']}")

def main():
    print("🔍 Calculando respuestas esperadas para consultas complejas...")
    
    # Cargar datos
    df = load_data()
    print(f"📋 Datos cargados: {len(df)} registros")
    
    # Calcular consultas complejas
    results = calculate_complex_queries(df)
    
    # Mostrar resumen
    print_summary(results)
    
    # Guardar resultados
    save_results(results)
    
    print(f"\n✅ Proceso completado. Se calcularon {len(results)} consultas complejas.")

if __name__ == "__main__":
    main()

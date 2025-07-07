#!/usr/bin/env python3
"""
Script para generar un archivo Excel demo más completo.
Incluye múltiples hojas con datos realistas para pruebas.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

def create_ventas_data():
    """Crea datos de ventas mensuales."""
    np.random.seed(42)
    
    # Generar fechas
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    
    # Productos
    productos = [
        'Laptop HP', 'Mouse Logitech', 'Teclado Mecánico', 'Monitor 24"',
        'Auriculares Sony', 'Webcam 1080p', 'Disco SSD 500GB', 'RAM 16GB',
        'Impresora Canon', 'Router WiFi', 'Cable HDMI', 'Hub USB'
    ]
    
    # Vendedores
    vendedores = [
        'Ana García', 'Carlos López', 'María Rodríguez', 'Juan Pérez',
        'Laura Martín', 'Pedro Sánchez', 'Carmen Ruiz', 'Miguel Torres'
    ]
    
    # Ciudades
    ciudades = [
        'Madrid', 'Barcelona', 'Valencia', 'Sevilla',
        'Bilbao', 'Málaga', 'Murcia', 'Las Palmas'
    ]
    
    # Generar datos
    data = []
    for _ in range(1500):  # 1500 registros de ventas
        fecha = random.choice(dates)
        producto = random.choice(productos)
        vendedor = random.choice(vendedores)
        ciudad = random.choice(ciudades)
        
        # Precios base por producto
        precios_base = {
            'Laptop HP': 850, 'Mouse Logitech': 25, 'Teclado Mecánico': 120,
            'Monitor 24"': 200, 'Auriculares Sony': 80, 'Webcam 1080p': 60,
            'Disco SSD 500GB': 90, 'RAM 16GB': 150, 'Impresora Canon': 180,
            'Router WiFi': 75, 'Cable HDMI': 15, 'Hub USB': 35
        }
        
        precio_base = precios_base[producto]
        cantidad = random.randint(1, 5)
        
        # Añadir variación al precio
        precio_unitario = precio_base * random.uniform(0.9, 1.1)
        precio_total = precio_unitario * cantidad
        
        # Descuento ocasional
        descuento = 0
        if random.random() < 0.15:  # 15% de probabilidad de descuento
            descuento = random.uniform(0.05, 0.20)
        
        precio_final = precio_total * (1 - descuento)
        
        data.append({
            'Fecha': fecha,
            'Producto': producto,
            'Vendedor': vendedor,
            'Ciudad': ciudad,
            'Cantidad': cantidad,
            'Precio_Unitario': round(precio_unitario, 2),
            'Precio_Total': round(precio_total, 2),
            'Descuento_Pct': round(descuento * 100, 1),
            'Precio_Final': round(precio_final, 2),
            'Mes': fecha.strftime('%Y-%m'),
            'Trimestre': f"Q{(fecha.month-1)//3 + 1}-{fecha.year}",
            'Estado': random.choice(['Completada', 'Pendiente', 'Cancelada']) 
                     if random.random() < 0.95 else 'Cancelada'
        })
    
    return pd.DataFrame(data)

def create_empleados_data():
    """Crea datos de empleados."""
    nombres = [
        'Ana García López', 'Carlos Martínez Ruiz', 'María José Rodríguez',
        'Juan Antonio Pérez', 'Laura Isabel Martín', 'Pedro Luis Sánchez',
        'Carmen María Ruiz', 'Miguel Ángel Torres', 'Isabel Fernández',
        'Roberto Carlos Jiménez', 'Lucía Morales Castro', 'David Romero'
    ]
    
    departamentos = [
        'Ventas', 'Marketing', 'IT', 'Recursos Humanos',
        'Finanzas', 'Operaciones', 'Atención Cliente'
    ]
    
    cargos = {
        'Ventas': ['Vendedor Junior', 'Vendedor Senior', 'Gerente Ventas'],
        'Marketing': ['Analista Marketing', 'Especialista Digital', 'Director Marketing'],
        'IT': ['Desarrollador', 'Analista Sistemas', 'CTO'],
        'Recursos Humanos': ['Generalista RRHH', 'Especialista Nómina', 'Director RRHH'],
        'Finanzas': ['Analista Financiero', 'Contador', 'CFO'],
        'Operaciones': ['Coordinador', 'Supervisor', 'Director Operaciones'],
        'Atención Cliente': ['Agente', 'Supervisor', 'Gerente Atención']
    }
    
    data = []
    for i, nombre in enumerate(nombres):
        departamento = random.choice(departamentos)
        cargo = random.choice(cargos[departamento])
        
        # Salarios base por cargo
        salarios_base = {
            'Junior': 28000, 'Senior': 42000, 'Analista': 35000,
            'Especialista': 38000, 'Coordinador': 33000, 'Supervisor': 45000,
            'Gerente': 55000, 'Director': 75000, 'CTO': 90000, 'CFO': 85000,
            'Agente': 25000, 'Generalista': 40000, 'Contador': 48000,
            'Desarrollador': 45000
        }
        
        # Determinar salario base
        salario = 35000  # default
        for keyword, sal in salarios_base.items():
            if keyword in cargo:
                salario = sal
                break
        
        # Añadir variación
        salario = salario * random.uniform(0.9, 1.15)
        
        fecha_ingreso = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1460))
        
        data.append({
            'ID_Empleado': f"EMP{i+1:03d}",
            'Nombre_Completo': nombre,
            'Departamento': departamento,
            'Cargo': cargo,
            'Salario_Anual': round(salario, 2),
            'Fecha_Ingreso': fecha_ingreso,
            'Años_Empresa': round((datetime.now() - fecha_ingreso).days / 365.25, 1),
            'Email': f"{nombre.split()[0].lower()}.{nombre.split()[1].lower()}@empresa.com",
            'Activo': random.choice([True, True, True, False])  # 75% activos
        })
    
    return pd.DataFrame(data)

def create_inventario_data():
    """Crea datos de inventario."""
    categorias = ['Electrónicos', 'Accesorios', 'Software', 'Componentes']
    
    productos_por_categoria = {
        'Electrónicos': ['Laptop Dell', 'Laptop HP', 'Tablet iPad', 'Smartphone Samsung'],
        'Accesorios': ['Mouse Logitech', 'Teclado Mecánico', 'Auriculares Sony', 'Webcam 4K'],
        'Software': ['Office 365', 'Adobe Creative', 'Windows 11', 'Antivirus Norton'],
        'Componentes': ['Disco SSD 1TB', 'RAM 32GB', 'Tarjeta Gráfica', 'Procesador Intel']
    }
    
    data = []
    for categoria, productos in productos_por_categoria.items():
        for producto in productos:
            stock_actual = random.randint(10, 200)
            stock_minimo = random.randint(5, 25)
            precio_compra = random.uniform(50, 800)
            precio_venta = precio_compra * random.uniform(1.3, 2.2)
            
            data.append({
                'Código_Producto': f"PROD{len(data)+1:04d}",
                'Nombre_Producto': producto,
                'Categoría': categoria,
                'Stock_Actual': stock_actual,
                'Stock_Mínimo': stock_minimo,
                'Precio_Compra': round(precio_compra, 2),
                'Precio_Venta': round(precio_venta, 2),
                'Margen_Beneficio': round(((precio_venta - precio_compra) / precio_compra) * 100, 1),
                'Estado_Stock': 'Crítico' if stock_actual <= stock_minimo else 
                              'Bajo' if stock_actual <= stock_minimo * 2 else 'Normal',
                'Proveedor': random.choice(['TechSupply', 'GlobalTech', 'ElectroWorld', 'ComponentesPro']),
                'Última_Compra': datetime.now() - timedelta(days=random.randint(1, 90))
            })
    
    return pd.DataFrame(data)

def main():
    """Función principal para generar el archivo Excel."""
    print("🚀 Generando archivo Excel demo completo...")
    
    # Crear DataFrames
    print("📊 Generando datos de ventas...")
    df_ventas = create_ventas_data()
    
    print("👥 Generando datos de empleados...")
    df_empleados = create_empleados_data()
    
    print("📦 Generando datos de inventario...")
    df_inventario = create_inventario_data()
    
    # Crear archivo Excel con múltiples hojas
    output_path = Path("data/default/empresa-demo.xlsx")
    print(f"💾 Guardando archivo en: {output_path}")
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Hoja principal - Resumen
        resumen_data = {
            'Métrica': [
                'Total Ventas', 'Número de Transacciones', 'Ticket Promedio',
                'Total Empleados', 'Empleados Activos', 'Departamentos',
                'Productos en Inventario', 'Valor Total Inventario'
            ],
            'Valor': [
                f"€{df_ventas['Precio_Final'].sum():,.2f}",
                len(df_ventas),
                f"€{df_ventas['Precio_Final'].mean():.2f}",
                len(df_empleados),
                len(df_empleados[df_empleados['Activo'] == True]),
                df_empleados['Departamento'].nunique(),
                len(df_inventario),
                f"€{(df_inventario['Stock_Actual'] * df_inventario['Precio_Compra']).sum():,.2f}"
            ],
            'Descripción': [
                'Suma total de todas las ventas', 'Número total de transacciones',
                'Valor promedio por transacción', 'Total de empleados registrados',
                'Empleados actualmente activos', 'Número de departamentos únicos',
                'Productos diferentes en inventario', 'Valor total del stock actual'
            ]
        }
        pd.DataFrame(resumen_data).to_excel(writer, sheet_name='Resumen', index=False)
        
        # Hojas de datos
        df_ventas.to_excel(writer, sheet_name='Ventas', index=False)
        df_empleados.to_excel(writer, sheet_name='Empleados', index=False)
        df_inventario.to_excel(writer, sheet_name='Inventario', index=False)
    
    print("✅ Archivo Excel generado exitosamente!")
    print(f"📈 Datos incluidos:")
    print(f"   - Ventas: {len(df_ventas)} registros")
    print(f"   - Empleados: {len(df_empleados)} registros")
    print(f"   - Inventario: {len(df_inventario)} productos")
    print(f"   - Hojas: Resumen, Ventas, Empleados, Inventario")

if __name__ == "__main__":
    main()

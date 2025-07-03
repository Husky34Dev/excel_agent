# Excel Chatbot 🤖📊

Un chatbot inteligente que responde preguntas complejas sobre archivos Excel usando Groq LLM y pandas en un sandbox seguro. **Ahora con soporte completo para múltiples hojas** y validaciones de seguridad avanzadas.

## ✨ Características Principales

### 🔄 **Manejo Inteligente de Múltiples Hojas**
- **Auto-detección**: Detecta automáticamente todas las hojas del Excel
- **Análisis combinado**: Puede combinar datos de múltiples hojas automáticamente
- **Selección inteligente**: Sugiere la mejor hoja para analizar
- **Joins automáticos**: Realiza relaciones entre hojas usando columnas comunes

### 🛡️ **Seguridad Avanzada**
- **Validación de imports**: Solo permite librerías seguras (pandas, numpy, etc.)
- **Sandbox aislado**: Ejecución en proceso separado con límites de recursos
- **Funciones bloqueadas**: Previene uso de `exec()`, `eval()`, `open()`, etc.
- **Timeout automático**: Límite de tiempo de ejecución (5 segundos)

### 🧠 **Inteligencia de Análisis**
- **Generación de código**: Usa Groq LLM para generar código pandas específico
- **Esquema automático**: Detecta columnas, tipos de datos y valores de muestra
- **Análisis temporal**: Soporte para fechas, trimestres, tendencias
- **Consultas complejas**: Estadísticas, correlaciones, outliers, etc.

### 💻 **Modos de Uso**
- **Chatbot interactivo**: Modo conversacional persistente
- **Consulta única**: Para análisis rápidos desde línea de comandos
- **Logging inteligente**: Terminal limpio + logs detallados a archivo

## 📋 Requisitos

- Python 3.8+
- Cuenta en [Groq Cloud](https://console.groq.com/) (API key gratuita)
- Windows, macOS o Linux

## 🚀 Instalación Rápida

1. **Clona el repositorio**
   ```bash
   git clone <repository-url>
   cd excel-chatbot
   ```

2. **Crea el entorno virtual**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**
   ```bash
   copy .env.example .env  # Windows
   # cp .env.example .env    # Linux/Mac
   ```
   
5. **Edita `.env`** y añade tu `GROQ_API_KEY` desde [Groq Console](https://console.groq.com/)

## 💡 Uso

### 🎯 **Modo Interactivo (Recomendado)**
```bash
# Chatbot interactivo con múltiples hojas automáticas
python main.py --interactive

# O simplemente
python main.py
```

### 📊 **Análisis de Múltiples Hojas**
```bash
# Ver todas las hojas disponibles
python main.py --list-sheets

# Usar una hoja específica
python main.py --sheet "Ventas" "¿Cuántas ventas hubo?"

# Análisis que combina múltiples hojas automáticamente
python main.py "¿Qué cliente ha comprado más productos?"
```

### ⚡ **Consultas Rápidas**
```bash
# Consultas simples
python main.py "¿Cuántas filas tiene el Excel?"
python main.py "¿Cuál es el promedio de ventas?"

# Análisis con múltiples hojas automático
python main.py "¿Qué cliente ha comprado más productos?"
python main.py "¿Cuántos clientes únicos hay en total?"

# Especificar archivo diferente
python main.py --file "mi_archivo.xlsx" "¿Cuántos registros hay?"
```

## 🔍 **Ejemplos de Consultas Avanzadas**

### 📊 **Análisis Multi-Hoja Automático**
```bash
# El sistema automáticamente combina hojas Ventas + Clientes + Productos
python main.py "¿En qué región se concentran más las ventas?"
python main.py "¿Cuál es el producto más vendido por región?"
python main.py "¿Qué cliente tiene el mayor volumen de compras?"
```

### 📈 **Análisis Temporal**
```bash
python main.py "¿En qué trimestre hubo mejores beneficios?"
python main.py "¿Cuál es la tendencia mensual de ingresos?"
python main.py "¿En qué mes se registraron los mayores ingresos totales?"
```

### 📋 **Estadísticas y Correlaciones**
```bash
python main.py "¿Cuál es la correlación entre ingresos y gastos?"
python main.py "¿Cuál es la región más eficiente?"
python main.py "¿Hay valores atípicos en los ingresos?"
```

### 🎛️ **Comandos Especiales (Modo Interactivo)**
- `ayuda` - Ver ejemplos de consultas
- `cambiar archivo` - Usar otro archivo Excel
- `salir` - Terminar el chatbot

## 🛡️ **Seguridad**

### ✅ **Características de Seguridad**
- **Imports limitados**: Solo pandas, numpy, datetime, math, etc.
- **Funciones bloqueadas**: `exec()`, `eval()`, `open()`, `os.system()`, etc.
- **Sandbox aislado**: Proceso separado con límites de recursos
- **Timeout automático**: Máximo 5 segundos de ejecución
- **Limpieza automática**: Archivos temporales se eliminan automáticamente

### 🚫 **Código Bloqueado Automáticamente**
```python
# ❌ Estos tipos de código son automáticamente rechazados:
import os                    # Import prohibido
exec("malicious_code")      # Función peligrosa
open("/etc/passwd")         # Acceso a archivos del sistema
requests.get("evil.com")    # Librerías de red no permitidas
```

## 📁 Estructura del Proyecto

```
excel-chatbot/
├── 📁 config/                    # Configuración y logging
│   ├── settings.py              # Variables de entorno
│   └── logger_config.py         # Configuración de logs
├── 📁 src/
│   ├── 📁 agent/                # Cerebro principal
│   │   ├── code_agent.py        # Orquestación principal
│   │   └── python_exec_tool.py  # Herramientas de ejecución
│   ├── 📁 executor/             # Ejecución segura
```

## ⚙️ **Configuración Avanzada**

### 🔧 **Variables de Entorno (.env)**

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `GROQ_API_KEY` | Tu clave de API de Groq Cloud (**requerida**) | - |
| `GROQ_MODEL` | Modelo LLM a usar | `llama-3.3-70b-versatile` |
| `SANDBOX_CPU_TIME` | Límite de CPU por ejecución (segundos) | `2` |
| `SANDBOX_MEMORY_BYTES` | Límite de memoria (bytes) | `200MB` |
| `EXCEL_DEFAULT_SHEET` | Hoja por defecto si no se especifica | `0` |

### 🎯 **Parámetros de Línea de Comandos**

```bash
# Opciones principales
python main.py [opciones] [pregunta]

# Opciones disponibles:
--interactive, -i     # Modo chatbot interactivo
--file, -f           # Especificar archivo Excel
--sheet, -s          # Usar hoja específica
--list-sheets        # Mostrar información de todas las hojas
--debug              # Modo debug con logs en terminal

# Ejemplos:
python main.py --file "ventas2024.xlsx" --sheet "Q1" "¿Cuál fue el mejor mes?"
python main.py --debug --interactive
python main.py --list-sheets --file "complejo.xlsx"
```

## 📊 **Tipos de Análisis Soportados**

### 📈 **Estadísticas Descriptivas**
- Promedios, medianas, desviaciones estándar
- Conteos y distribuciones
- Valores mínimos y máximos
- Percentiles y cuartiles

### 🔗 **Análisis Relacional (Multi-Hoja)**
- Joins automáticos entre hojas
- Análisis de clientes y productos
- Seguimiento de transacciones
- Inventarios y stocks

### ⏰ **Análisis Temporal**
- Tendencias por mes, trimestre, año
- Comparaciones período a período
- Estacionalidad y patrones
- Rangos de fechas

### 🎯 **Análisis Avanzado**
- Correlaciones entre variables
- Detección de valores atípicos (outliers)
- Análisis de eficiencia
- Ratios y métricas personalizadas

## 🧪 **Testing y Validación**

### 🔬 **Ejecutar Tests**
```bash
# Test de seguridad
python test_security.py

# Test de múltiples hojas
python test_multi_sheet_functionality.py

# Test de consultas complejas
python tests/calculate_expected_results.py
```

### 📋 **Validación de Resultados**
El sistema incluye tests automáticos con consultas pre-calculadas para verificar la precisión de las respuestas.

## 🚨 **Troubleshooting**

### ❓ **Problemas Comunes**

**Error: "GROQ_API_KEY no está definida"**
- Verifica que el archivo `.env` existe y contiene tu API key
- Reactiva el entorno virtual

**Error: "Archivo Excel no encontrado"**
- Verifica la ruta del archivo
- Usa rutas absolutas si es necesario
- Usa `--list-sheets` para verificar el archivo

**Error: "Código rechazado por seguridad"**
- El sistema detectó código potencialmente peligroso
- Revisa los logs para más detalles
- Solo se permiten análisis de datos con pandas/numpy

**Error: "Timeout después de X segundos"**
- La consulta es muy compleja o el archivo muy grande
- Simplifica la pregunta o usa una muestra más pequeña

### � **Logs Detallados**
```bash
# Los logs se guardan automáticamente en:
logs/excel_chatbot.log

# Para ver logs en tiempo real:
tail -f logs/excel_chatbot.log  # Linux/Mac
Get-Content logs/excel_chatbot.log -Wait  # Windows PowerShell
```

## 🤝 **Contribuir**

1. Fork el repositorio
2. Crea tu rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📜 **Licencia**

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 **Agradecimientos**

- [Groq](https://groq.com/) por proporcionar LLM rápidos y gratuitos
- [Pandas](https://pandas.pydata.org/) por la potente biblioteca de análisis de datos
- Comunidad de Python por las herramientas increíbles

---

**¿Preguntas o problemas?** Abre un [issue](../../issues) en GitHub.

**¿Te gusta el proyecto?** ¡Dale una ⭐ en GitHub!
| `SANDBOX_CPU_TIME` | Límite de CPU en segundos | `2` |
| `SANDBOX_MEMORY_BYTES` | Límite de memoria en bytes | `209715200` |
| `EXCEL_DEFAULT_SHEET` | Hoja por defecto a cargar | `0` |

## 🛠️ Herramientas Incluidas

- **`inspect_excel.py`**: Inspecciona la estructura de tus archivos Excel
- **`verify_calculations.py`**: Verifica la precisión de las respuestas del chatbot

## 🎯 Casos de Uso Soportados

- ✅ Análisis básicos (promedios, sumas, conteos)
- ✅ Filtrado por fechas y regiones
- ✅ Análisis temporal (trimestres, meses, años)
- ✅ Cálculos de márgenes y porcentajes
- ✅ Estadísticas descriptivas
- ✅ Comparaciones entre períodos
- ✅ Rankings y top N resultados
- `GROQ_MODEL`: Modelo a usar (default: llama-3.3-70b-versatile)
- `SANDBOX_CPU_TIME`: Límite de CPU en segundos (default: 2)
- `SANDBOX_MEMORY_BYTES`: Límite de memoria en bytes (default: 200MB)
- `SANDBOX_USER`: Usuario para sandbox Unix (default: nobody)
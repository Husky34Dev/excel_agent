# 🤖 Excel Chatbot - Consultas Instantáneas con IA

Sistema inteligente para hacer consultas en archivos Excel usando IA y pandas. Optimizado para archivos grandes con sistema de caché persistente.

## ✨ Características

- 🚀 **Carga única**: El Excel se carga una sola vez y queda en memoria
- ⚡ **Consultas instantáneas**: Sin recargar datos entre consultas  
- 🧠 **IA inteligente**: Genera código pandas automáticamente
- 🛡️ **Seguro**: Sandbox para ejecución controlada de código
- 💾 **Caché persistente**: Los datos se mantienen entre sesiones
- 📊 **Archivos grandes**: Optimizado para datasets de cientos de miles de filas

## 🔧 Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd excel-chatbot
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tu GROQ_API_KEY
```

## 🚀 Uso

### Modo interactivo (recomendado):
```bash
python main.py
```

### Consulta única:
```bash
python main.py "¿Cuántas filas tiene el Excel?"
```

### Con archivo específico:
```bash
python main.py --file mi_archivo.xlsx "¿Cuál es el promedio de ventas?"
```

## 💡 Ejemplos de consultas

```
• ¿Cuántas filas tiene el Excel?
• ¿Cuál es el teléfono que ha recibido más llamadas?
• ¿Cuál es el tiempo promedio de llamada?
• ¿Cuántas llamadas hay por campaña?
• ¿En qué hora del día se hacen más llamadas?
• ¿Qué porcentaje de llamadas fueron contestadas?
```

## 📁 Estructura del proyecto

```
excel-chatbot/
├── main.py                    # Punto de entrada
├── src/
│   ├── agent/                 # Agente principal con IA
│   ├── cache/                 # Sistema de caché persistente
│   ├── executor/              # Sandbox para ejecución segura
│   └── loader/                # Carga de archivos Excel/CSV
├── config/                    # Configuración y logging
├── data/input/               # Archivos de datos (no se suben a git)
└── logs/                     # Logs de la aplicación
```

## ⚙️ Configuración

El sistema se configura a través de `config/settings.py` y variables de entorno:

- `GROQ_API_KEY`: Tu clave API de Groq (requerida)
- `GROQ_MODEL`: Modelo a usar (default: llama-3.3-70b-versatile)
- `SANDBOX_CPU_TIME`: Tiempo máximo de CPU (default: 5s)
- `SANDBOX_MEMORY_BYTES`: Memoria máxima (default: 200MB)

## 🔒 Seguridad

- Sandbox aislado para ejecución de código
- Whitelist de imports permitidos
- Validación de sintaxis y AST
- Límites de CPU y memoria
- Auto-limpieza de archivos temporales

## 📊 Rendimiento

- **Archivos pequeños** (<10k filas): ~1-2 segundos por consulta
- **Archivos medianos** (10k-100k filas): ~2-3 segundos por consulta  
- **Archivos grandes** (>100k filas): ~3-5 segundos por consulta
- **Carga inicial**: Una sola vez, luego consultas instantáneas

## 🛠️ Desarrollo

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📝 Licencia

MIT License - Ver archivo LICENSE para detalles.

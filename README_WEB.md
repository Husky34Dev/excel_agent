# 🌐 Excel Chatbot - Interfaz Web

## ✨ Nueva Funcionalidad: Interfaz Web Moderna

La aplicación ahora incluye una interfaz web completa que complementa la aplicación de línea de comandos existente.

### 🚀 Cómo usar la interfaz web

#### 1. Instalar dependencias adicionales
```bash
pip install -r requirements.txt
```

#### 2. Ejecutar el servidor web
```bash
python web.py
```

#### 3. Abrir en navegador
- **Interfaz principal**: http://localhost:8000
- **API docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

### 🏗️ Características

#### 🏢 **Multi-Cliente**
- Selector desplegable con todos los clientes configurados
- Información dinámica del cliente seleccionado
- Preguntas de ejemplo específicas por dominio

#### 📁 **Gestión de Archivos**
- **Drag & Drop**: Arrastra archivos Excel directamente
- **Upload inteligente**: Se guardan automáticamente en la carpeta del cliente
- **Lista de archivos**: Visualiza todos los archivos disponibles por cliente
- **Selector de archivo**: Cambia entre archivos sin recargar

#### 💬 **Chat Interactivo**
- Interfaz de chat moderna y responsive
- Preguntas de ejemplo clicables
- Indicador de "escribiendo" durante procesamiento
- Tiempo de ejecución mostrado en respuestas
- Clear chat para empezar de nuevo

#### 🎨 **UI/UX**
- Diseño moderno con Tailwind CSS
- Responsive (móvil y desktop)
- Iconos Font Awesome
- Animaciones suaves
- Notificaciones de éxito/error

### 🏛️ Arquitectura

```
core/web/
├── app.py              # FastAPI app principal
├── routes/
│   ├── api.py          # Endpoints de consultas
│   └── upload.py       # Manejo de archivos
└── static/
    ├── css/            # Estilos (Tailwind CDN)
    └── js/
        └── app.js      # JavaScript principal

templates/
└── index.html          # Template principal
```

### 🔗 Endpoints API

#### **GET /** 
- Página principal con interfaz web

#### **GET /api/clients**
- Lista todos los clientes disponibles

#### **GET /api/clients/{client_id}/files**
- Archivos disponibles para un cliente

#### **POST /api/query**
- Procesar consulta del usuario
```json
{
  "question": "¿Cuántas filas tiene el dataset?",
  "client_id": "default",
  "file_path": "data/default/demo.xlsx"
}
```

#### **POST /upload/file**
- Subir archivo Excel para un cliente
- FormData: `file` + `client_id`

#### **GET /health**
- Health check del servidor

### 🔧 Configuración

La interfaz web utiliza la misma configuración que la aplicación CLI:
- Clientes definidos en `clients/`
- Variables de entorno en `.env`
- Configuración en `config/settings.py`

### 🎯 Flujo de Uso

1. **Seleccionar Cliente**: Desplegable superior derecho
2. **Subir/Seleccionar Excel**: Drag & drop o lista de archivos
3. **Hacer Consultas**: Chat interactivo con el agente
4. **Ver Resultados**: Respuestas formateadas con tiempo de ejecución

### 🤝 Integración

La interfaz web **NO modifica** la aplicación CLI existente:
- ✅ `python main.py` sigue funcionando igual
- ✅ Toda la lógica de negocio se reutiliza
- ✅ Mismos clientes, mismos agentes, misma configuración
- ✅ Arquitectura modular preservada

### 📊 Beneficios

- **🚀 Experiencia de usuario mejorada**: Interfaz visual intuitiva
- **📱 Accesibilidad**: Usar desde cualquier dispositivo con navegador
- **👥 Multi-usuario**: Varios usuarios pueden acceder simultáneamente
- **🔄 Gestión de archivos**: Upload y organización simplificada
- **📈 Productividad**: Consultas más rápidas y visuales

---

### 💡 Próximos pasos sugeridos

- [ ] Autenticación y roles de usuario
- [ ] Visualización de gráficos en respuestas
- [ ] Historial de consultas persistente
- [ ] Exportar resultados a Excel/PDF
- [ ] Websockets para real-time updates
- [ ] Configuración de clientes via web

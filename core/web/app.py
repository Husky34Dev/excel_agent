"""
Aplicación web FastAPI para Excel Chatbot.
Proporciona una interfaz web moderna que utiliza toda la arquitectura modular existente.
"""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from pathlib import Path

from core.client_manager import ClientManager
from core.web.routes.api import router as api_router
from core.web.routes.upload import router as upload_router

# Configurar paths
BASE_DIR = Path(__file__).parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="Excel Chatbot Web Interface",
    description="Interfaz web moderna para análisis inteligente de Excel",
    version="2.0.0"
)

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Incluir rutas
app.include_router(api_router, prefix="/api")
app.include_router(upload_router, prefix="/upload")

# Instancia global del client manager
client_manager = ClientManager()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal de la aplicación web."""
    # Obtener lista de clientes disponibles
    clients = client_manager.list_clients()
    client_configs = {}
    
    for client_id in clients:
        try:
            config = client_manager.load_client_config(client_id)
            client_configs[client_id] = {
                "name": config.client_name,
                "description": config.description,
                "banner_title": config.ui_config.get("banner_title", ""),
                "banner_subtitle": config.ui_config.get("banner_subtitle", ""),
                "example_questions": config.ui_config.get("example_questions", [])
            }
        except Exception as e:
            print(f"Error loading client {client_id}: {e}")
            continue
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "clients": client_configs
    })

@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {"status": "healthy", "service": "excel-chatbot-web"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
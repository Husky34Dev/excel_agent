"""
Rutas API para el chatbot Excel.
Maneja las consultas y la interacción con el agente.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import os
from pathlib import Path

from core.client_manager import ClientManager, ClientConfig
from core.agent.base_agent import BaseAgent
from config.settings import get_settings

router = APIRouter()

# Instancias globales
client_manager = ClientManager()
current_agents: Dict[str, BaseAgent] = {}  # Cache de agentes por sesión

class QueryRequest(BaseModel):
    question: str
    client_id: str
    file_path: Optional[str] = None
    sheet_name: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

@router.get("/clients")
async def get_clients():
    """Obtener lista de clientes disponibles."""
    try:
        clients = client_manager.list_clients()
        client_data = {}
        
        for client_id in clients:
            try:
                config = client_manager.load_client_config(client_id)
                client_data[client_id] = {
                    "name": config.client_name,
                    "description": config.description,
                    "banner_title": config.ui_config.get("banner_title", ""),
                    "example_questions": config.ui_config.get("example_questions", []),
                    "workspace_folder": config.get_workspace_folder()
                }
            except Exception as e:
                continue
        
        return {"success": True, "clients": client_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clients/{client_id}/files")
async def get_client_files(client_id: str):
    """Obtener archivos disponibles para un cliente."""
    try:
        config = client_manager.load_client_config(client_id)
        workspace_folder = config.get_workspace_folder()
        
        if not os.path.exists(workspace_folder):
            return {"success": True, "files": []}
        
        files = []
        for file_path in Path(workspace_folder).glob("*.xlsx"):
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size
                })
        
        return {"success": True, "files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Procesar una consulta del usuario."""
    import time
    start_time = time.time()
    
    try:
        # Obtener o crear agente para el cliente
        agent = await get_or_create_agent(request.client_id)
        
        # Determinar archivo a usar
        file_path = request.file_path
        if not file_path:
            config = client_manager.load_client_config(request.client_id)
            file_path = config.get_default_file()
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=400, detail="Archivo no encontrado")
        
        # Procesar consulta
        result = agent.ask(file_path, request.question, request.sheet_name)
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            success=True,
            result=result,
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return QueryResponse(
            success=False,
            error=str(e),
            execution_time=execution_time
        )

async def get_or_create_agent(client_id: str) -> BaseAgent:
    """Obtener o crear un agente para el cliente especificado."""
    if client_id not in current_agents:
        config = client_manager.load_client_config(client_id)
        settings = get_settings()
        
        agent = BaseAgent(
            client_config=config,
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            cpu_time=settings.sandbox_cpu_time,
            memory_bytes=settings.sandbox_memory_bytes,
            sandbox_user=settings.sandbox_user
        )
        
        current_agents[client_id] = agent
    
    return current_agents[client_id]

@router.post("/clear-cache/{client_id}")
async def clear_cache(client_id: str):
    """Limpiar caché para un cliente específico."""
    try:
        if client_id in current_agents:
            current_agents[client_id].clear_cache()
            del current_agents[client_id]
        
        return {"success": True, "message": "Cache cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

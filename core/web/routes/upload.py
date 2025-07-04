"""
Rutas para manejo de archivos y uploads.
Permite subir archivos Excel y organizarlos por cliente.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
import shutil
import os
from typing import List

from core.client_manager import ClientManager

router = APIRouter()
client_manager = ClientManager()

@router.post("/file")
async def upload_file(
    file: UploadFile = File(...),
    client_id: str = Form(...)
):
    """
    Subir un archivo Excel para un cliente específico.
    El archivo se guarda automáticamente en la carpeta del cliente.
    """
    try:
        # Validar cliente
        config = client_manager.load_client_config(client_id)
        workspace_folder = Path(config.get_workspace_folder())
        
        # Crear carpeta si no existe
        workspace_folder.mkdir(parents=True, exist_ok=True)
        
        # Validar tipo de archivo
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400, 
                detail="Solo se permiten archivos Excel (.xlsx, .xls)"
            )
        
        # Generar path del archivo
        file_path = workspace_folder / file.filename
        
        # Guardar archivo
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "success": True,
            "message": f"Archivo '{file.filename}' subido exitosamente",
            "file_path": str(file_path),
            "client_id": client_id,
            "file_size": len(content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/file")
async def delete_file(file_path: str, client_id: str):
    """Eliminar un archivo específico."""
    try:
        # Validar cliente
        config = client_manager.load_client_config(client_id)
        workspace_folder = Path(config.get_workspace_folder())
        
        # Validar que el archivo esté en la carpeta del cliente
        file_path_obj = Path(file_path)
        try:
            # Verificar que el archivo esté dentro del workspace del cliente
            file_path_obj.resolve().relative_to(workspace_folder.resolve())
        except ValueError:
            raise HTTPException(
                status_code=403, 
                detail="No se puede eliminar archivos fuera del workspace del cliente"
            )
        
        # Eliminar archivo
        if file_path_obj.exists():
            file_path_obj.unlink()
            return {
                "success": True,
                "message": f"Archivo eliminado: {file_path_obj.name}"
            }
        else:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/validate")
async def validate_upload_limits():
    """Obtener límites y validaciones para uploads."""
    return {
        "max_file_size_mb": 50,
        "allowed_extensions": [".xlsx", ".xls"],
        "max_files_per_client": 10
    }

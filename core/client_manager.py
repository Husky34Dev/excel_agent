"""
Sistema de configuración de clientes para Excel Agent.
Permite personalizar la aplicación para diferentes clientes sin cambiar código.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ClientConfig:
    """Configuración completa de un cliente."""
    client_name: str
    client_id: str
    description: str
    ui_config: Dict[str, Any]
    data_config: Dict[str, Any]
    prompts_config: Dict[str, Any]
    
    @classmethod
    def from_json_file(cls, config_path: str) -> 'ClientConfig':
        """Carga configuración desde archivo JSON."""
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(
            client_name=data.get('client_name', 'Excel Agent'),
            client_id=data.get('client_id', 'default'),
            description=data.get('description', ''),
            ui_config=data.get('ui', {}),
            data_config=data.get('data', {}),
            prompts_config=data.get('prompts', {})
        )
    
    def get_banner(self) -> str:
        """Genera el banner personalizado."""
        title = self.ui_config.get('banner_title', '🤖 EXCEL AGENT')
        subtitle = self.ui_config.get('banner_subtitle', 'Análisis Inteligente de Datos')
        
        banner = "=" * 70 + "\n"
        banner += f"{title}\n"
        banner += f"{subtitle}\n"
        banner += "=" * 70 + "\n"
        banner += "⚡ DataFrame precargado en memoria para consultas súper rápidas\n"
        banner += "📝 Escribe 'salir', 'exit' o 'quit' para terminar\n"
        banner += "📊 Escribe 'cambiar archivo' para usar otro Excel\n"
        banner += "🔍 Escribe 'ayuda' para ver ejemplos de consultas\n"
        banner += "📈 Escribe 'stats' para ver estadísticas del caché\n"
        banner += "=" * 70
        
        return banner
    
    def get_help_examples(self) -> List[str]:
        """Obtiene ejemplos de consultas personalizados."""
        return self.ui_config.get('example_questions', [
            "¿Cuántas filas tiene el Excel?",
            "¿Cuál es el promedio de la primera columna numérica?"
        ])
    
    def get_default_file(self) -> Optional[str]:
        """Obtiene el archivo Excel por defecto para este cliente."""
        return self.ui_config.get('default_file')
    
    def get_workspace_folder(self) -> str:
        """Obtiene la carpeta de trabajo para este cliente."""
        return self.data_config.get('workspace_folder', 'data/default')
    
    def get_specialized_prompt_context(self) -> str:
        """Obtiene contexto especializado para los prompts."""
        context = self.prompts_config.get('domain_context', '')
        instructions = self.prompts_config.get('specialized_instructions', [])
        
        if instructions:
            context += "\n\nINSTRUCCIONES ESPECIALIZADAS:\n"
            for instruction in instructions:
                context += f"- {instruction}\n"
        
        return context

class ClientManager:
    """Gestor de configuraciones de clientes."""
    
    def __init__(self, clients_dir: str = "clients"):
        self.clients_dir = Path(clients_dir)
        self.clients_dir.mkdir(exist_ok=True)
        self._create_default_config()
    
    def _create_default_config(self):
        """Crea configuración por defecto si no existe."""
        default_path = self.clients_dir / "default.json"
        if not default_path.exists():
            default_config = {
                "client_name": "Excel Agent - Genérico",
                "client_id": "default",
                "description": "Configuración genérica para análisis de Excel",
                "ui": {
                    "banner_title": "🤖 EXCEL AGENT",
                    "banner_subtitle": "Análisis Inteligente de Datos Excel",
                    "welcome_message": "Sistema genérico para análisis de datos Excel",
                    "default_file": "data/input/demo.xlsx",
                    "example_questions": [
                        "¿Cuántas filas tiene el Excel?",
                        "¿Cuáles son las columnas disponibles?",
                        "¿Cuál es el promedio de la primera columna numérica?",
                        "¿Hay valores nulos en los datos?",
                        "¿Cuáles son los valores únicos de la primera columna de texto?"
                    ]
                },
                "data": {
                    "workspace_folder": "data/input",
                    "auto_detect_columns": True,
                    "expected_columns": {}
                },
                "prompts": {
                    "domain_context": "Datos genéricos de Excel sin dominio específico",
                    "specialized_instructions": [
                        "Usar nombres de columnas exactos como aparecen en el dataset",
                        "Manejar valores nulos apropiadamente",
                        "Proporcionar resultados claros y concisos"
                    ]
                }
            }
            
            with open(default_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
    
    def list_clients(self) -> List[str]:
        """Lista todos los clientes disponibles."""
        return [f.stem for f in self.clients_dir.glob("*.json")]
    
    def load_client_config(self, client_id: str) -> ClientConfig:
        """Carga configuración de un cliente específico."""
        config_path = self.clients_dir / f"{client_id}.json"
        
        if not config_path.exists():
            # Fallback a configuración por defecto
            config_path = self.clients_dir / "default.json"
            
        return ClientConfig.from_json_file(str(config_path))
    
    def auto_detect_client(self, data_folder: str) -> str:
        """Auto-detecta cliente basado en la carpeta de datos."""
        # Lógica simple: buscar si hay un cliente que use esa carpeta
        for client_file in self.clients_dir.glob("*.json"):
            try:
                config = ClientConfig.from_json_file(str(client_file))
                if config.get_workspace_folder() == data_folder:
                    return config.client_id
            except:
                continue
        
        return "default"

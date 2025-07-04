#!/usr/bin/env python3
"""
Punto de entrada para la interfaz web del Excel Chatbot.
Ejecuta el servidor web FastAPI con la configuración adecuada.
"""
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para imports
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def main():
    """Función principal para ejecutar el servidor web."""
    try:
        import uvicorn
        from core.web.app import app
        
        print("🚀 Iniciando Excel Chatbot Web Interface...")
        print("📱 Interfaz disponible en: http://localhost:8000")
        print("📋 API docs en: http://localhost:8000/docs")
        print("⚡ Para parar el servidor: Ctrl+C")
        print("-" * 50)
        
        # Configuración del servidor
        uvicorn.run(
            "core.web.app:app",  # Import string para reload
            host="0.0.0.0",
            port=8000,
            reload=True,  # Auto-reload en desarrollo
            log_level="info"
        )
        
    except ImportError as e:
        print("❌ Error: Dependencias web no instaladas")
        print("💡 Ejecuta: pip install -r requirements.txt")
        print(f"Detalle: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Servidor detenido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

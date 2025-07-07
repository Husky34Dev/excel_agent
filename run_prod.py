#!/usr/bin/env python3
"""
Script para producción - ejecutar el servidor web sin auto-reload.
Uso: python run_prod.py
"""
import os
import subprocess
import sys
from pathlib import Path

def main():
    """Ejecutar el servidor web en modo producción."""
    print("🚀 Iniciando Excel Chatbot en modo producción...")
    print("📱 Interfaz disponible en: http://localhost:8000")
    print("📋 API docs en: http://localhost:8000/docs")
    print("⚡ Para parar el servidor: Ctrl+C")
    print("-" * 50)
    
    try:
        # Ejecutar sin auto-reload para producción
        cmd = [
            sys.executable, "-m", "uvicorn",
            "core.web.app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--workers", "1",
            "--log-level", "info"
        ]
        
        print(f"Ejecutando: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n⚠️ Servidor detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando uvicorn: {e}")
        print("💡 Asegúrate de que uvicorn esté instalado: pip install uvicorn")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()

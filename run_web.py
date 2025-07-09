#!/usr/bin/env python3
"""
Script para ejecutar el servidor web con uvicorn directamente.
Uso: python run_web.py
"""
import os
import subprocess
import sys
from pathlib import Path

def main():
    """Ejecutar el servidor web usando uvicorn directamente."""
    print("🚀 Iniciando Excel Chatbot Web Interface con uvicorn...")
    print("📱 Interfaz disponible en: http://localhost:8000")
    print("📋 API docs en: http://localhost:8000/docs")
    print("⚡ Para parar el servidor: Ctrl+C")
    print("-" * 50)
    
    try:
        # Ejecutar uvicorn con configuración simplificada y robusta
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "core.web.app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--reload-dir", "core",
            "--reload-dir", "templates", 
            "--reload-dir", "config",
            "--log-level", "info"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⚠️ Servidor detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando uvicorn: {e}")
        print("💡 Asegúrate de que uvicorn esté instalado: pip install uvicorn")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
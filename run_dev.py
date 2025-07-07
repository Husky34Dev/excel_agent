#!/usr/bin/env python3
"""
Script para desarrollo - ejecutar el servidor web con uvicorn con monitoreo limitado.
Uso: python run_dev.py
"""
import os
import subprocess
import sys
from pathlib import Path

def main():
    """Ejecutar el servidor web para desarrollo."""
    print("🚀 Iniciando Excel Chatbot en modo desarrollo...")
    print("📱 Interfaz disponible en: http://localhost:8000")
    print("📋 API docs en: http://localhost:8000/docs")
    print("⚡ Para parar el servidor: Ctrl+C")
    print("-" * 50)
    
    try:
        # Usar watchfiles con patrones específicos para evitar reinicios innecesarios
        cmd = [
            sys.executable, "-m", "uvicorn",
            "core.web.app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--reload-dir", "core",
            "--reload-dir", "templates", 
            "--reload-dir", "config",
            "--reload-dir", "clients",
            "--reload-include", "*.py",
            "--reload-include", "*.html",
            "--reload-include", "*.js",
            "--reload-include", "*.css",
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

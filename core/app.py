"""
Módulo principal de la aplicación Excel Chatbot.
Maneja toda la lógica de negocio, argumentos, y flujo de sesión.
"""
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from config.settings import get_settings
from config.logger_config import configure_logging, configure_file_only_logging, get_logger
from core.agent.base_agent import BaseAgent
from utils import parse_output, ExecutionError, CodeAgentError, LoaderError
from core.client_manager import ClientManager, ClientConfig


class ExcelChatbotApp:
    """Aplicación principal del chatbot Excel."""
    
    def __init__(self):
        self.client_manager = ClientManager()
        self.logger = None
        self.agent = None
        self.client_config = None
        
    def create_argument_parser(self):
        """Crear y configurar el parser de argumentos."""
        parser = argparse.ArgumentParser(
            description="Chatbot interactivo para consultas complejas sobre Excel",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Modos de uso:
  python main.py                              # Modo interactivo
  python main.py "¿Cuál es el promedio?"      # Consulta única
  python main.py --file datos.xlsx            # Especificar archivo
  python main.py --debug                      # Modo debug
            """
        )
        parser.add_argument(
            "question",
            nargs="*",
            help="Pregunta sobre los datos del Excel (opcional para modo interactivo)"
        )
        parser.add_argument(
            "--file", "-f",
            default="data/input/demo.xlsx",
            help="Ruta al archivo Excel (default: data/input/demo.xlsx)"
        )
        parser.add_argument(
            "--sheet", "-s",
            default=None,
            help="Nombre o índice de la hoja del Excel a usar (auto-detecta la mejor si no se especifica)"
        )
        parser.add_argument(
            "--list-sheets",
            action="store_true",
            help="Mostrar información de todas las hojas del Excel y salir"
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Activar modo debug con logging detallado en terminal"
        )
        parser.add_argument(
            "--client", "-c",
            default="default",
            help="ID del cliente a usar (default: default). Usa 'list' para ver clientes disponibles"
        )
        parser.add_argument(
            "--list-clients",
            action="store_true",
            help="Mostrar clientes disponibles y salir"
        )
        
        return parser
    
    def setup_logging(self, debug_mode: bool):
        """Configurar el sistema de logging."""
        # Crear directorio de logs si no existe
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configurar logging - siempre a archivo, solo a terminal si debug
        log_level = "DEBUG" if debug_mode else "INFO"
        
        if debug_mode:
            configure_logging(level=log_level)  # A terminal y archivo
        else:
            # Solo a archivo
            configure_file_only_logging(level=log_level)
        
        self.logger = get_logger(__name__)
        self.logger.info("="*50)
        self.logger.info("INICIANDO SESIÓN DEL CHATBOT EXCEL")
        self.logger.info("="*50)
    
    def list_clients_command(self):
        """Ejecutar comando de listar clientes."""
        clients = self.client_manager.list_clients()
        print("\n🏢 CLIENTES DISPONIBLES:")
        print("=" * 50)
        for client_id in clients:
            try:
                config = self.client_manager.load_client_config(client_id)
                print(f"📋 {client_id}")
                print(f"   Nombre: {config.client_name}")
                print(f"   Descripción: {config.description}")
                print(f"   Carpeta de datos: {config.get_workspace_folder()}")
                print("")
            except Exception as e:
                print(f"📋 {client_id} (error cargando config: {e})")
    
    def list_sheets_command(self, file_path: str):
        """Ejecutar comando de listar hojas."""
        try:
            from core.loader.multi_sheet_handler import analyze_excel_file
            analyze_excel_file(file_path)
        except Exception as e:
            print(f"❌ Error al analizar archivo: {e}")
    
    def load_client_config(self, client_id: str) -> bool:
        """Cargar configuración del cliente."""
        try:
            self.client_config = self.client_manager.load_client_config(client_id)
            print(f"✅ Cliente cargado: {self.client_config.client_name}")
            return True
        except Exception as e:
            print(f"❌ Error cargando cliente '{client_id}': {e}")
            print("💡 Usa --list-clients para ver clientes disponibles")
            return False
    
    def resolve_excel_file(self, file_arg: str) -> str:
        """Resolver la ruta del archivo Excel a usar."""
        # Verificar que el archivo Excel existe (usar default del cliente si no se especifica)
        if not file_arg or file_arg == "data/input/demo.xlsx":
            # Usar archivo por defecto del cliente
            default_file = self.client_config.get_default_file()
            if default_file and Path(default_file).exists():
                return default_file
        
        if not Path(file_arg).exists():
            print(f"❌ Error: Archivo no encontrado: {file_arg}")
            return None
        
        return file_arg
    
    def initialize_agent(self):
        """Inicializar el agente con la configuración actual."""
        try:
            settings = get_settings()
            self.logger.info(f"Iniciando agente con modelo {settings.groq_model}")
            
            self.agent = BaseAgent(
                client_config=self.client_config,
                api_key=settings.groq_api_key,
                model=settings.groq_model,
                cpu_time=settings.sandbox_cpu_time,
                memory_bytes=settings.sandbox_memory_bytes,
                sandbox_user=settings.sandbox_user
            )
            
            print(f"✅ Agente iniciado correctamente con modelo {settings.groq_model}")
            print(f"📄 Logs guardados en: logs/excel_chatbot.log")
            return True
            
        except Exception as e:
            print(f"💥 Error inicializando agente: {str(e)}")
            self.logger.exception("Error inicializando agente")
            return False
    
    def process_question(self, excel_path: str, question: str, specific_sheet=None):
        """Procesar una pregunta del usuario."""
        try:
            self.logger.info(f"Procesando pregunta: {question}")
            result = self.agent.ask(excel_path, question, sheet_name=specific_sheet)
            return result, None
        except LoaderError as e:
            error_msg = f"Error al cargar el archivo Excel: {str(e)}"
            self.logger.error(error_msg)
            return None, error_msg
        except ExecutionError as e:
            error_msg = f"Error de ejecución: {e.stderr}"
            self.logger.error(error_msg)
            return None, error_msg
        except CodeAgentError as e:
            error_msg = f"Error del agente: {str(e)}"
            self.logger.error(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            self.logger.exception(error_msg)
            return None, error_msg
    
    def run_single_query_mode(self, excel_path: str, question: str, specific_sheet=None):
        """Ejecutar modo de consulta única."""
        self.logger.info(f"Archivo Excel: {excel_path}")
        self.logger.info(f"Pregunta: {question}")

        # Inicializar agente
        if not self.initialize_agent():
            return False

        # Procesar pregunta
        result, error = self.process_question(excel_path, question, specific_sheet)
        
        if result:
            print("✅ Resultado:")
            print(result)
            return True
        else:
            print(f"❌ {error}")
            return False
    
    def run_interactive_mode(self, excel_path: str, specific_sheet=None):
        """Ejecutar modo interactivo."""
        from core.session import InteractiveSession
        
        # Inicializar agente
        if not self.initialize_agent():
            return False
        
        # Crear y ejecutar sesión interactiva
        session = InteractiveSession(
            agent=self.agent,
            client_config=self.client_config,
            client_manager=self.client_manager,
            logger=self.logger
        )
        
        return session.run(excel_path, specific_sheet)
    
    def run(self, args=None):
        """Punto de entrada principal de la aplicación."""
        # Parsear argumentos
        parser = self.create_argument_parser()
        if args is None:
            args = parser.parse_args()
        else:
            args = parser.parse_args(args)
        
        # Comando especial: listar clientes
        if args.list_clients or args.client == "list":
            self.list_clients_command()
            return True
        
        # Cargar configuración del cliente
        if not self.load_client_config(args.client):
            return False
        
        # Resolver archivo Excel
        excel_path = self.resolve_excel_file(args.file)
        if not excel_path:
            return False
        
        # Comando especial: solo listar hojas
        if args.list_sheets:
            self.list_sheets_command(excel_path)
            return True
        
        # Configurar logging
        self.setup_logging(args.debug)
        
        try:
            # Modo de una sola consulta
            if args.question:
                question = " ".join(args.question)
                return self.run_single_query_mode(excel_path, question, args.sheet)
            
            # Modo interactivo
            return self.run_interactive_mode(excel_path, args.sheet)
                
        except KeyboardInterrupt:
            print("\n⚠️ Cancelado por el usuario")
            return True
        except Exception as e:
            print(f"💥 Error inesperado: {str(e)}")
            if self.logger:
                self.logger.exception("Error inesperado en aplicación")
            if args.debug:
                import traceback
                traceback.print_exc()
            return False

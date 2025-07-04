"""
Módulo para manejar sesiones interactivas del chatbot Excel.
Contiene toda la lógica para el modo conversacional con comandos especiales.
"""
from pathlib import Path
from core.client_manager import ClientManager, ClientConfig


class InteractiveSession:
    """Maneja la sesión interactiva del chatbot Excel."""
    
    def __init__(self, agent, client_config: ClientConfig, client_manager: ClientManager, logger):
        self.agent = agent
        self.client_config = client_config
        self.client_manager = client_manager
        self.logger = logger
        self.question_count = 0
    
    def print_banner(self):
        """Mostrar banner personalizado del cliente."""
        print(self.client_config.get_banner())
    
    def print_help(self):
        """Mostrar ejemplos de consultas personalizados."""
        examples = self.client_config.get_help_examples()
        print("\n📚 EJEMPLOS DE CONSULTAS:")
        print("-" * 50)
        for example in examples:
            print(f"• {example}")
        print("\n🔧 COMANDOS ESPECIALES:")
        print("• 'stats' o 'cache' - Ver estadísticas del caché")
        print("• 'clear cache' - Limpiar caché en memoria")
        print("• 'cambiar archivo' - Usar otro archivo Excel")
        print("• 'cambiar cliente' - Cambiar configuración de cliente")
        print("-" * 50)
    
    def get_excel_file(self):
        """Solicitar archivo Excel al usuario."""
        default_file = self.client_config.get_default_file() or "data/input/demo.xlsx"
        
        while True:
            excel_path = input(f"\n📁 Ingresa la ruta del archivo Excel (Enter para usar {default_file}): ").strip()
            if not excel_path:
                excel_path = default_file
            
            if Path(excel_path).exists():
                return excel_path
            else:
                print(f"❌ Archivo no encontrado: {excel_path}")
                print("💡 Asegúrate de que la ruta sea correcta")
    
    def select_client(self) -> str:
        """Permite al usuario seleccionar un cliente."""
        clients = self.client_manager.list_clients()
        
        print("\n🏢 CLIENTES DISPONIBLES:")
        print("-" * 30)
        for i, client_id in enumerate(clients, 1):
            try:
                config = self.client_manager.load_client_config(client_id)
                print(f"{i}. {client_id} - {config.client_name}")
            except:
                print(f"{i}. {client_id}")
        print("-" * 30)
        
        while True:
            try:
                choice = input("Selecciona cliente (número o ID): ").strip()
                
                # Si es un número
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(clients):
                        return clients[idx]
                
                # Si es un ID directo
                if choice in clients:
                    return choice
                
                print("❌ Selección inválida. Intenta de nuevo.")
                
            except KeyboardInterrupt:
                return "default"
    
    def process_question(self, excel_path: str, question: str, specific_sheet=None):
        """Procesar una pregunta del usuario."""
        try:
            self.logger.info(f"Procesando pregunta: {question}")
            result = self.agent.ask(excel_path, question, sheet_name=specific_sheet)
            return result, None
        except Exception as e:
            # Los errores específicos se manejan en app.py
            error_msg = f"Error procesando pregunta: {str(e)}"
            self.logger.error(error_msg)
            return None, error_msg
    
    def preload_dataframe(self, excel_path: str, specific_sheet=None):
        """Precargar DataFrame automáticamente."""
        print(f"\n🔄 Precargando DataFrame automáticamente...")
        print(f"📂 Archivo: {excel_path}")
        
        if not self.agent.preload_dataframe(excel_path, specific_sheet):
            print("❌ Error precargando DataFrame. Continuando con carga bajo demanda.")
            self.logger.warning("Error en precarga, usando carga bajo demanda")
            return False
        else:
            # Mostrar estadísticas del caché
            cache_stats = self.agent.get_cache_stats()
            print(f"✅ DataFrame precargado exitosamente:")
            print(f"   💾 Memoria utilizada: ~{cache_stats.get('memory_usage_mb', 0):.1f} MB")
            print(f"   📂 Caché persistente: {'Sí' if cache_stats.get('has_disk_cache') else 'No'}")
            print(f"   ⚡ Sistema listo")
            return True
    
    def handle_special_commands(self, question: str, excel_path: str, specific_sheet=None):
        """Manejar comandos especiales. Retorna True si es un comando especial."""
        question_lower = question.lower()
        
        # Comando salir
        if question_lower in ['salir', 'exit', 'quit', 'q']:
            print("👋 ¡Hasta luego!")
            self.logger.info("Sesión terminada por el usuario")
            return 'exit'
        
        # Comando ayuda
        elif question_lower in ['ayuda', 'help', 'h']:
            self.print_help()
            return 'continue'
        
        # Comando cambiar archivo
        elif question_lower in ['cambiar archivo', 'cambiar', 'archivo']:
            new_excel_path = self.get_excel_file()
            print(f"📊 Archivo cambiado a: {new_excel_path}")
            self.logger.info(f"Archivo cambiado a: {new_excel_path}")
            
            # Precargar nuevo archivo
            print(f"🔄 Precargando nuevo DataFrame...")
            if self.agent.preload_dataframe(new_excel_path, specific_sheet):
                cache_stats = self.agent.get_cache_stats()
                print(f"✅ Nuevo DataFrame cargado: {cache_stats.get('rows', 0):,} filas")
            
            return ('file_changed', new_excel_path)
        
        # Comando estadísticas
        elif question_lower in ['stats', 'estadisticas', 'cache']:
            self.show_cache_stats()
            return 'continue'
        
        # Comando cambiar cliente
        elif question_lower in ['cambiar cliente', 'cliente', 'config']:
            self.change_client()
            return 'continue'
        
        # Comando limpiar caché
        elif question_lower in ['clear cache', 'limpiar cache', 'clear']:
            self.agent.clear_cache()
            print("🧹 Caché limpiado exitosamente")
            return 'continue'
        
        # No es un comando especial
        return False
    
    def show_cache_stats(self):
        """Mostrar estadísticas del caché."""
        cache_stats = self.agent.get_cache_stats()
        if cache_stats.get('loaded', False):
            print(f"\n📊 ESTADÍSTICAS DEL CACHÉ:")
            print(f"   📁 Archivo: {cache_stats.get('file_path', 'N/A')}")
            print(f"   📏 Filas: {cache_stats.get('rows', 0):,}")
            print(f"   📋 Columnas: {cache_stats.get('columns', 0)}")
            print(f"   💾 Memoria: ~{cache_stats.get('memory_usage_mb', 0):.1f} MB")
            print(f"   🕐 Cargado: {cache_stats.get('load_time', 'N/A')}")
            print(f"   📂 Caché en disco: {'Sí' if cache_stats.get('has_disk_cache') else 'No'}")
            if cache_stats.get('file_size_mb'):
                print(f"   📦 Tamaño archivo: {cache_stats.get('file_size_mb', 0):.1f} MB")
        else:
            print("📊 No hay DataFrame cargado en caché")
    
    def change_client(self):
        """Cambiar configuración de cliente."""
        new_client_id = self.select_client()
        try:
            new_client_config = self.client_manager.load_client_config(new_client_id)
            self.agent.update_client_config(new_client_config)
            self.client_config = new_client_config  # Actualizar referencia local
            print(f"✅ Cliente cambiado a: {self.client_config.client_name}")
            self.print_banner()
        except Exception as e:
            print(f"❌ Error cambiando cliente: {e}")
    
    def validate_excel_file(self, excel_path: str) -> str:
        """Validar y obtener archivo Excel para usar."""
        # Obtener archivo Excel
        if Path(excel_path).exists():
            print(f"📊 Usando archivo: {excel_path}")
            return excel_path
        else:
            if excel_path == "data/input/demo.xlsx":
                # Archivo demo por defecto
                print(f"📊 Usando archivo demo: {excel_path}")
                if not Path(excel_path).exists():
                    print(f"❌ Archivo demo no encontrado: {excel_path}")
                    return self.get_excel_file()
            else:
                print(f"❌ Archivo especificado no encontrado: {excel_path}")
                return self.get_excel_file()
        
        return excel_path
    
    def run(self, excel_path: str, specific_sheet=None):
        """Ejecutar la sesión interactiva."""
        try:
            # Mostrar banner
            self.print_banner()
            
            # Validar archivo Excel
            excel_path = self.validate_excel_file(excel_path)
            self.logger.info(f"Archivo Excel seleccionado: {excel_path}")
            
            # Precargar DataFrame
            self.preload_dataframe(excel_path, specific_sheet)
            
            # Loop principal del chatbot
            while True:
                try:
                    # Solicitar pregunta
                    print(f"\n{'='*50}")
                    question = input("🤖 Tu pregunta: ").strip()
                    
                    # Validar entrada vacía
                    if not question:
                        print("💡 Por favor, escribe una pregunta o 'ayuda' para ver ejemplos")
                        continue
                    
                    # Manejar comandos especiales
                    special_result = self.handle_special_commands(question, excel_path, specific_sheet)
                    if special_result == 'exit':
                        break
                    elif special_result == 'continue':
                        continue
                    elif isinstance(special_result, tuple) and special_result[0] == 'file_changed':
                        excel_path = special_result[1]
                        continue
                    
                    # Procesar pregunta normal
                    self.question_count += 1
                    print(f"\n🔍 Analizando... (Pregunta #{self.question_count})")
                    
                    result, error = self.process_question(excel_path, question, specific_sheet)
                    
                    if result:
                        print(f"\n✅ Resultado:")
                        print("-" * 30)
                        print(result)
                        print("-" * 30)
                        self.logger.info(f"Pregunta #{self.question_count} procesada exitosamente")
                    else:
                        print(f"\n❌ Error: {error}")
                        self.logger.error(f"Error en pregunta #{self.question_count}: {error}")
                    
                except KeyboardInterrupt:
                    print("\n⚠️ Operación cancelada. Escribe 'salir' para terminar.")
                    self.logger.info("Operación cancelada por usuario con Ctrl+C")
                    continue
            
            return True
            
        except Exception as e:
            error_msg = f"💥 Error fatal en sesión interactiva: {str(e)}"
            print(error_msg)
            self.logger.exception("Error fatal en sesión interactiva")
            return False

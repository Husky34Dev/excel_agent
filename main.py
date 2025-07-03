import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from config.settings import get_settings
from config.logger_config import configure_logging, get_logger
from src.agent.code_agent import CodeAgent
from src.utils import parse_output, ExecutionError, CodeAgentError, LoaderError

def print_banner():
    """Mostrar banner del chatbot"""
    print("=" * 70)
    print("🤖 EXCEL CHATBOT - Consultas Inteligentes sobre datos Excel")
    print("=" * 70)
    print("💡 Haz preguntas complejas sobre tus datos Excel")
    print("📝 Escribe 'salir', 'exit' o 'quit' para terminar")
    print("📊 Escribe 'cambiar archivo' para usar otro Excel")
    print("🔍 Escribe 'ayuda' para ver ejemplos de consultas")
    print("=" * 70)

def print_help():
    """Mostrar ejemplos de consultas"""
    print("\n📚 EJEMPLOS DE CONSULTAS:")
    print("-" * 50)
    print("• ¿Cuántas filas tiene el Excel?")
    print("• ¿Cuál es la región con mayor beneficio total?")
    print("• ¿Cuál es el promedio de margen de beneficio por región?")
    print("• ¿En qué mes se registraron los mayores ingresos?")
    print("• ¿Cuál es la correlación entre ingresos y gastos?")
    print("• ¿Cuál es la región más eficiente?")
    print("• ¿Cuál fue el trimestre con mejores beneficios?")
    print("• Muestra las primeras 10 filas")
    print("• ¿Cuáles son las estadísticas descriptivas?")
    print("-" * 50)

def get_excel_file():
    """Solicitar archivo Excel al usuario"""
    while True:
        excel_path = input("\n📁 Ingresa la ruta del archivo Excel (Enter para usar demo.xlsx): ").strip()
        if not excel_path:
            excel_path = "data/input/demo.xlsx"
        
        if Path(excel_path).exists():
            return excel_path
        else:
            print(f"❌ Archivo no encontrado: {excel_path}")
            print("💡 Asegúrate de que la ruta sea correcta")

def process_question(agent, excel_path, question, logger, specific_sheet=None):
    """Procesar una pregunta del usuario"""
    try:
        logger.info(f"Procesando pregunta: {question}")
        if specific_sheet:
            result = agent.ask(excel_path, question, specific_sheet=specific_sheet)
        else:
            result = agent.ask(excel_path, question)
        return result, None
    except LoaderError as e:
        error_msg = f"Error al cargar el archivo Excel: {str(e)}"
        logger.error(error_msg)
        return None, error_msg
    except ExecutionError as e:
        error_msg = f"Error de ejecución: {e.stderr}"
        logger.error(error_msg)
        return None, error_msg
    except CodeAgentError as e:
        error_msg = f"Error del agente: {str(e)}"
        logger.error(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        logger.exception(error_msg)
        return None, error_msg

def main():
    """Función principal del chatbot Excel."""
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
        "--interactive", "-i",
        action="store_true",
        help="Forzar modo interactivo aunque se proporcione una pregunta"
    )
    
    args = parser.parse_args()
    
    # Verificar que el archivo Excel existe
    if not Path(args.file).exists():
        print(f"❌ Error: Archivo no encontrado: {args.file}")
        return
    
    # Modo especial: solo listar hojas
    if args.list_sheets:
        try:
            from src.loader.multi_sheet_handler import analyze_excel_file
            analyze_excel_file(args.file)
            return
        except Exception as e:
            print(f"❌ Error al analizar archivo: {e}")
            return
    
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar logging - siempre a archivo, solo a terminal si debug
    log_level = "DEBUG" if args.debug else "INFO"
    
    if args.debug:
        configure_logging(level=log_level)  # A terminal y archivo
    else:
        # Solo a archivo
        from config.logger_config import configure_file_only_logging
        configure_file_only_logging(level=log_level)
    
    logger = get_logger(__name__)
    logger.info("="*50)
    logger.info("INICIANDO SESIÓN DEL CHATBOT EXCEL")
    logger.info("="*50)

    # Modo de una sola consulta
    if args.question and not args.interactive:
        question = " ".join(args.question)
        excel_path = args.file

        # Verificar que el archivo Excel existe
        if not Path(excel_path).exists():
            print(f"❌ Error: Archivo no encontrado: {excel_path}")
            return

        try:
            # Cargar configuración
            settings = get_settings()
            logger.info(f"Iniciando agente con modelo {settings.groq_model}")
            logger.info(f"Archivo Excel: {excel_path}")
            logger.info(f"Pregunta: {question}")

            # Inicializar agente
            agent = CodeAgent(
                api_key=settings.groq_api_key,
                model=settings.groq_model,
                cpu_time=settings.sandbox_cpu_time,
                memory_bytes=settings.sandbox_memory_bytes,
                sandbox_user=settings.sandbox_user
            )

            # Procesar pregunta
            result, error = process_question(agent, excel_path, question, logger, specific_sheet=args.sheet)
            
            if result:
                print("✅ Resultado:")
                print(result)
            else:
                print(f"❌ {error}")
                
        except KeyboardInterrupt:
            print("\n⚠️ Cancelado por el usuario")
        except Exception as e:
            print(f"💥 Error inesperado: {str(e)}")
            logger.exception("Error inesperado en modo consulta única")
        return

    # Modo interactivo
    print_banner()
    
    # Obtener archivo Excel
    if Path(args.file).exists():
        excel_path = args.file
        print(f"📊 Usando archivo: {excel_path}")
    else:
        if args.file != "data/input/demo.xlsx":
            print(f"❌ Archivo especificado no encontrado: {args.file}")
        excel_path = get_excel_file()
    
    logger.info(f"Archivo Excel seleccionado: {excel_path}")

    try:
        # Cargar configuración e inicializar agente
        settings = get_settings()
        logger.info(f"Iniciando agente con modelo {settings.groq_model}")
        
        agent = CodeAgent(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            cpu_time=settings.sandbox_cpu_time,
            memory_bytes=settings.sandbox_memory_bytes,
            sandbox_user=settings.sandbox_user
        )
        
        print(f"✅ Agente iniciado correctamente con modelo {settings.groq_model}")
        print(f"📄 Logs guardados en: logs/excel_chatbot.log")

        # Loop principal del chatbot
        question_count = 0
        while True:
            try:
                # Solicitar pregunta
                print(f"\n{'='*50}")
                question = input("🤖 Tu pregunta: ").strip()
                
                # Comandos especiales
                if question.lower() in ['salir', 'exit', 'quit', 'q']:
                    print("👋 ¡Hasta luego!")
                    logger.info("Sesión terminada por el usuario")
                    break
                elif question.lower() in ['ayuda', 'help', 'h']:
                    print_help()
                    continue
                elif question.lower() in ['cambiar archivo', 'cambiar', 'archivo']:
                    excel_path = get_excel_file()
                    print(f"📊 Archivo cambiado a: {excel_path}")
                    logger.info(f"Archivo cambiado a: {excel_path}")
                    continue
                elif not question:
                    print("💡 Por favor, escribe una pregunta o 'ayuda' para ver ejemplos")
                    continue
                
                question_count += 1
                print(f"\n🔍 Analizando... (Pregunta #{question_count})")
                
                # Procesar pregunta
                result, error = process_question(agent, excel_path, question, logger, specific_sheet=args.sheet)
                
                if result:
                    print(f"\n✅ Resultado:")
                    print("-" * 30)
                    print(result)
                    print("-" * 30)
                    logger.info(f"Pregunta #{question_count} procesada exitosamente")
                else:
                    print(f"\n❌ Error: {error}")
                    logger.error(f"Error en pregunta #{question_count}: {error}")
                
            except KeyboardInterrupt:
                print("\n⚠️ Operación cancelada. Escribe 'salir' para terminar.")
                logger.info("Operación cancelada por usuario con Ctrl+C")
                continue
                
    except Exception as e:
        error_msg = f"💥 Error fatal: {str(e)}"
        print(error_msg)
        logger.exception("Error fatal en modo interactivo")
        if args.debug:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

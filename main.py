"""
Punto de entrada principal del chatbot Excel.
Delega toda la lógica de negocio a core.app.
"""
from core.app import ExcelChatbotApp


def main():
    """Función principal - punto de entrada limpio."""
    app = ExcelChatbotApp()
    success = app.run()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()

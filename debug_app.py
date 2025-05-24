from app import create_app
import traceback
import sys

print("Iniciando depuración de create_app()...")

try:
    app = create_app()
    print("create_app() ejecutado correctamente.")
except Exception as e:
    print(f"ERROR en create_app(): {e}")
    print("Detalles completos del error:")
    traceback.print_exc()
    sys.exit(1)
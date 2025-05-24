from app import create_app
import os
import sys
import traceback

print("DEBUG: Iniciando run.py...")

try:
    print("DEBUG: Llamando a create_app()...")
    app = create_app()
    print("DEBUG: create_app() finalizado. Objeto 'app' creado.")
except Exception as e:
    print(f"ERROR: Ocurrió un error durante create_app(): {e}")
    traceback.print_exc()
    sys.exit(1)  # Salida controlada con código de error

if __name__ == '__main__':
    print("DEBUG: Dentro del bloque if __name__ == '__main__'.")

    # Configuración del host, puerto y modo de depuración
    # Asegurarse de que el host no incluya el protocolo http://
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    if host.startswith('http://'):
        host = host.replace('http://', '')
    
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']

    print(f"DEBUG: Intentando iniciar app.run() en host={host}, port={port}, debug={debug_mode}")
    try:
        app.run(host=host, port=port, debug=debug_mode)
    except Exception as e:
        print(f"ERROR: Ocurrió un error durante app.run(): {e}")
        traceback.print_exc()
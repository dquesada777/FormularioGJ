from app import create_app
import os
import sys
import traceback
    
app = create_app()
    
if __name__ == '__main__':
    
    # Configuración del host, puerto y modo de depuración
    # Asegurarse de que el host no incluya el protocolo http://
    host = '127.0.0.1'
    debug_mode = True
    port = 5000
        
    try:
        app.run(host=host, port=port, debug=debug_mode)
    except Exception as e:
        print(f"ERROR: Ocurrió un error durante app.run(): {e}")
        traceback.print_exc()
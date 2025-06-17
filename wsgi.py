import os
from app import create_app

# Determinar el entorno (desarrollo o producción)
env = os.environ.get('FLASK_ENV', 'production')

# Crear la aplicación con la configuración adecuada
app = create_app(env)

if __name__ == '__main__':
    app.run()
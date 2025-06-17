import os
from dotenv import load_dotenv

load_dotenv()  # Carga variables de entorno desde .env

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ba862647ba11624698c9986974edf7d8b5e178db46950071889c1b4c68660a87')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'

class ProductionConfig(Config):
    DEBUG = False
    # Usar una ruta absoluta para la base de datos SQLite en producción
    # Esto asegura que la base de datos tenga permisos de escritura
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join('/tmp', 'app.db')

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
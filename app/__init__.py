from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv

load_dotenv() # Carga variables de entorno desde .env

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=True)

    # Cargar configuración según el entorno
    from config import config
    app.config.from_object(config[config_name])

    # Asegurarse de que el directorio de la base de datos existe y tiene permisos
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not db_path.startswith('/'):  # Si es una ruta relativa
            db_path = os.path.join(app.instance_path, db_path)
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'main.login' # 'main' es el nombre del blueprint, 'login' la función de vista
    login_manager.login_message_category = 'info'

    with app.app_context():
        # Registrar el blueprint
        from .routes import main_bp
        app.register_blueprint(main_bp)
        
        from . import models   # Importar modelos
        db.create_all() # Crea las tablas si no existen
        return app
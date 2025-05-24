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

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Configuración de la aplicación
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ba862647ba11624698c9986974edf7d8b5e178db46950071889c1b4c68660a87')
    
    # Usar SQLite en lugar de MySQL para pruebas
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
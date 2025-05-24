print("Verificando importaciones...")

try:
    print("Importando Flask...")
    from flask import Flask
    print("Flask importado correctamente.")
    
    print("Importando SQLAlchemy...")
    from flask_sqlalchemy import SQLAlchemy
    print("SQLAlchemy importado correctamente.")
    
    print("Importando LoginManager...")
    from flask_login import LoginManager
    print("LoginManager importado correctamente.")
    
    print("Importando CSRFProtect...")
    from flask_wtf.csrf import CSRFProtect
    print("CSRFProtect importado correctamente.")
    
    print("Importando mysql.connector...")
    import mysql.connector
    print("mysql.connector importado correctamente.")
    
    print("Importando dotenv...")
    from dotenv import load_dotenv
    print("dotenv importado correctamente.")
    
    print("Importando openpyxl...")
    import openpyxl
    print("openpyxl importado correctamente.")
    
    print("Todas las importaciones funcionan correctamente.")
except ImportError as e:
    print(f"ERROR: No se pudo importar: {e}")
except Exception as e:
    print(f"ERROR inesperado: {e}")
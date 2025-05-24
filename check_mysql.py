import mysql.connector
import sys

print("Intentando conectar a MySQL...")

try:
    # Intenta conectar a MySQL con los parámetros por defecto de la aplicación
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""  # Sin contraseña por defecto
    )
    print("Conexión a MySQL exitosa!")
    
    # Verificar si la base de datos existe
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES LIKE 'inmobiliariadb'")
    result = cursor.fetchone()
    
    if result:
        print("La base de datos 'inmobiliariadb' existe.")
        
        # Intentar usar la base de datos
        cursor.execute("USE inmobiliariadb")
        print("Conexión a la base de datos 'inmobiliariadb' exitosa.")
        
        # Verificar tablas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"Tablas en la base de datos: {tables}")
    else:
        print("La base de datos 'inmobiliariadb' NO existe.")
        print("Esto podría ser la causa del problema.")
    
    conn.close()
    
except mysql.connector.Error as err:
    print(f"ERROR: No se pudo conectar a MySQL: {err}")
    print("Este es probablemente el problema que impide que tu aplicación funcione.")
    sys.exit(1)
except Exception as e:
    print(f"ERROR inesperado: {e}")
    sys.exit(1)
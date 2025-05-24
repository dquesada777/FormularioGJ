import mysql.connector
import sys

print("Verificando conexión a la base de datos MySQL...")

try:
    # Intenta conectar a MySQL con los parámetros de la aplicación
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Ajusta esto si tu MySQL tiene contraseña
        database="inmobiliariadb"
    )
    print("¡Conexión exitosa a la base de datos inmobiliariadb!")
    
    # Verificar tablas existentes
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    
    print("Tablas encontradas en la base de datos:")
    for table in tables:
        print(f"- {table[0]}")
    
    conn.close()
    print("Conexión cerrada correctamente.")
    
except mysql.connector.Error as err:
    print(f"ERROR: No se pudo conectar a MySQL: {err}")
    print("Verifica que:")
    print("1. El servidor MySQL esté en ejecución")
    print("2. La base de datos 'inmobiliariadb' exista")
    print("3. El usuario 'root' tenga acceso sin contraseña (o ajusta la contraseña en el script)")
    sys.exit(1)
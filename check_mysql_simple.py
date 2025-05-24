import mysql.connector

print("Intentando conectar a MySQL...")

try:
    # Intenta conectar a MySQL con los parámetros por defecto de la aplicación
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""  # Sin contraseña por defecto
    )
    print("Conexión a MySQL exitosa!")
    conn.close()
except Exception as e:
    print(f"ERROR: No se pudo conectar a MySQL: {e}")
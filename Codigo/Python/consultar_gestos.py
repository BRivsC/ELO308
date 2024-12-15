import sqlite3
import os

# Conectar a la base de datos SQLite
db_path = 'registro_datos_1ch.db'
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en: {os.path.abspath(db_path)}")

# Consultar los datos de gesto_id, fecha y gesto, omitiendo los gesto_id repetidos
cursor.execute("""
    SELECT gesto_id, MIN(fecha), gesto 
    FROM datos 
    GROUP BY gesto_id
""")
datos = cursor.fetchall()

# Imprimir los datos obtenidos por consola
for fila in datos:
    gesto_id, fecha, gesto = fila
    print(f"Gesto: {gesto}\t Fecha: {fecha}\t ID: {gesto_id}  ")

# Cerrar la conexión a la base de datos
conexion.close()

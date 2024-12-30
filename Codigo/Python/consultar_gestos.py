''' Consultar gestos

Script en Python para consultar qué gestos existen en la base de datos.
Tras ejecutarlo retorna por consola la ID única, fecha de captura y el nombre de
cada gesto registrado.
Bastián Rivas
'''
import sqlite3
import os

# Conectar a la base de datos SQLite
db_path = 'Datos/datos_gestos_3ch.db'
nombre_tabla = 'raw'
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en: {os.path.abspath(db_path)}")

# Consultar los datos de gesto_id, fecha y gesto, omitiendo gesto_id repetidos
cursor.execute(f"""
    SELECT gesto_id, MIN(fecha), nombre_gesto, sesion_id 
    FROM {nombre_tabla} 
    GROUP BY gesto_id
""")
datos = cursor.fetchall()

# Imprimir los datos obtenidos por consola
print(f"""--- Gestos registrados ---
ID  \tFecha              \tSesión\tNombre del gesto
----\t-------------------\t------\t----------------
""")
for fila in datos:
    gesto_id, fecha, gesto, sesion_id = fila
    print(f"{gesto_id}\t{fecha}\t{sesion_id}\t{gesto}")

# Cerrar la conexión a la base de datos
conexion.close()

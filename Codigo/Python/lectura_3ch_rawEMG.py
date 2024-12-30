''' Lectura de 3 canales EMG bruto

Script en Python para registrar los datos de EMG recibidos desde el puerto 
tserial
Espera recibirlos con el formato <onset>,<CH1>,<CH2>,<CH3>,...

Estructura de la base de datos
------------------------------
          id: Identificador único autoincremental para cada entrada
    gesto_id: Identificador único para cada gesto. Útil para diferenciar 
              distintas instancias del mismo gesto
   sesion_id: Número de la sesión en que se registró el gesto
       onset: Indicador de si se está ejecutando el gesto. 1 para indicar que 
              está en ejecución
nombre_gesto: Nombre del gesto hecho
          fs: Frecuencia de muestreo en Hertz
       fecha: Fecha en la que se hizo la captura, YYYY-MM-DD HH:MM:SS
         CHX: Valor recibido para el canal X sin pasar por filtros

Uso
---
    - Ejecutar e ingresar el número de la sesión actual, o pulsar Enter para 
    mantener el último usado
    - Mantener pulsado botón en la placa mientras se hace el gesto
    - Hacer 1 repetición de 1 gesto por vez
    - Al terminar la toma de datos pulsar Ctrl+C

Bastián Rivas
'''

import serial
import sqlite3
import time
from datetime import datetime
import os

# Función para insertar datos en la base de datos en lotes
def insertar_datos_lote(datos):
    cursor.executemany("""INSERT INTO datos (gesto_id, sesion_id, nombre_gesto,
                          onset, CH1, CH2, CH3, fecha, fs) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", datos)
    conexion.commit()

# Configurar el puerto serial
puerto_serial = 'COM4'
baud_rate = 115200

# Frecuencia de muestreo en Hz
fs = 1000

# Conectar o crear la base de datos SQLite
db_path = 'Datos/datos_gestos_3ch.db'
nombre_tabla = 'raw'
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en: {os.path.abspath(db_path)}")

# Crear la tabla si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS datos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gesto_id INTEGER,
                    sesion_id INTEGER,
                    onset INTEGER,
                    nombre_gesto TEXT,
                    fs INTEGER,
                    fecha TEXT,
                    CH1 INTEGER,
                    CH2 INTEGER,
                    CH3 INTEGER
                )''')

# Obtener el último gesto_id y sesion_id registrados en la base de datos

cursor.execute(f"""SELECT MAX(gesto_id), nombre_gesto, sesion_id 
                    FROM {nombre_tabla}""")
ultimo_registro = cursor.fetchone()
ultimo_gesto_id = ultimo_registro[0] if ultimo_registro[0] is not None else 0
if ultimo_registro[1] is not None:
    ultimo_nombre_gesto = ultimo_registro[1] 
else:
    ultimo_nombre_gesto ="N/A" 

ultimo_sesion_id = ultimo_registro[2] if ultimo_registro[2] is not None else 1
gesto_id = (ultimo_gesto_id + 1) if ultimo_gesto_id is not None else 1

# Solicitar el sesion_id al usuario
print(f"Última sesión registrada con ID = {ultimo_sesion_id}")
sesion_id = input("Por favor, ingrese el número de sesión: ")
sesion_id = int(sesion_id) if sesion_id else ultimo_sesion_id

# Solicitar el nombre del gesto al usuario
print(f"Último gesto registrado fue '{ultimo_nombre_gesto}' con 
ID = {ultimo_gesto_id}")
nombre_gesto = input("Por favor, ingrese el nombre del gesto: ")
fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Lista para almacenar los datos leídos
# Uso un lote acá porque escribir directamente en la base de datos es demasiado 
# lento
datos_lote = []  

# Abrir el puerto serial y comenzar a leer datos
try:
    with serial.Serial(puerto_serial, baud_rate, timeout=1) as ser:
        print(f"Leyendo desde {puerto_serial} a {baud_rate} baud...
              \nFinalizar con Ctrl+C")
        while True:
            # Leer línea desde el puerto serial
            if ser.in_waiting > 0:
                try:
                    data = ser.readline().decode('ascii').rstrip()
                    valores = data.split(',')

                    # Asegurarse de que hay cuatro valores
                    # Formato: onset, ch1, ch2, ch3
                    if len(valores) == 4:
                        try:
                            onset = int(valores[0])
                            ch1 = int(valores[1])
                            ch2 = int(valores[2])
                            ch3 = int(valores[3])
                            datos_lote.append((gesto_id, sesion_id, 
                                               nombre_gesto, onset, ch1, ch2, 
                                               ch3, fecha, fs))
                            print(f"Registrado Onset: {onset}\t CH1: {ch1}\t 
                                    CH2: {ch2}\t CH3: {ch3}")

                            # Insertar en la base de datos en lotes de 
                            # 100 registros
                            if len(datos_lote) >= 100:
                                insertar_datos_lote(datos_lote)
                                # Limpiar la lista después de insertar
                                datos_lote = []  
                        except ValueError:
                            print(f"Error al convertir los datos a enteros: 
                            {data}")
                    else:
                        print(f"Datos incompletos recibidos: {data}")

                except UnicodeDecodeError:
                    # Suele caer acá cuando registra datos incompletos desde el 
                    # puerto serial. Típicamente pasa si empieza a leer cuando 
                    # se está recibiendo una línea
                    pass

except serial.SerialException as e:
    print(f"Error al acceder al puerto serial: {e}")
except KeyboardInterrupt:
    print(f"\nLectura interrumpida. Datos guardados en {db_path}")
    # Insertar cualquier dato restante en la base de datos
    if datos_lote:
        insertar_datos_lote(datos_lote)

# Cerrar la conexión a la base de datos
finally:
    conexion.close()

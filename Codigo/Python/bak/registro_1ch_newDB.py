'''
Script en Python para registrar los datos de EMG recibidos desde el puerto serial
Espera recibirlos con el formato <CH1_filtrado>,<CH1_envolvente>,<CH2_filtrado>,...
Estructura de la base de datos:
          id: Identificador único autoincremental para cada entrada
    gesto_id: Identificador único para cada gesto. Útil para diferenciar distintas instancias del mismo gesto
     CHX_fil: Valor recibido para el canal X luego de pasar por el filtro corriendo desde el microcontrolador
     CHX_env: Valor recibido de la envolvente (aprox) del canal X 
   timestamp: ms desde que se capturó el primer dato
       fecha: Fecha en la que se hizo la captura, YYYY-MM-DD HH:MM:SS
       gesto: Nombre del gesto hecho

Uso: Ejecutar e ingresar nombre del gesto a hacer.
     Hacer 1 repetición de 1 gesto por vez!
     Al terminar la toma de datos, finalizar con Ctrl+C
'''


import serial
import sqlite3
import time
from datetime import datetime
import os

# Configurar el puerto serial
puerto_serial = 'COM3'
baud_rate = 115200

# Conectar o crear la base de datos SQLite
db_path = 'registro_datos_1ch.db'
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en: {os.path.abspath(db_path)}")

# Crear la tabla si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS datos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gesto_id INTEGER,
                    CH1_fil INTEGER,
                    CH1_env INTEGER,
                    timestamp INTEGER,
                    fecha TEXT,
                    gesto TEXT
                )''')

# Inicializar variables de tiempo y gesto
gesto = input("Por favor, define el gesto para este registro: ")
gesto_id = int(time.time() * 1000)  # Definir gesto_id con el timestamp inicial
start_time = None  # Tiempo de referencia para calcular el timestamp relativo

# Función para insertar datos en la base de datos
def insertar_dato(ch1_fil, ch1_env):
    global start_time
    
    # Si es el primer dato recibido, inicializamos el tiempo de referencia
    if start_time is None:
        start_time = time.time() * 1000  # Milisegundos

    # Calcular milisegundos transcurridos desde el primer dato
    timestamp = int(time.time() * 1000 - start_time)
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("INSERT INTO datos (gesto_id, CH1_fil, CH1_env, timestamp, fecha, gesto) VALUES (?, ?, ?, ?, ?, ?)", 
                   (gesto_id, ch1_fil, ch1_env, timestamp, fecha, gesto))
    conexion.commit()

# Abrir el puerto serial y comenzar a leer datos
try:
    with serial.Serial(puerto_serial, baud_rate, timeout=1) as ser:
        print(f"Leyendo desde {puerto_serial} a {baud_rate} baud...\n")
        while True:
            # Leer línea desde el puerto serial
            if ser.in_waiting > 0:
                data = ser.readline().decode('ascii').rstrip()
                valores = data.split(',')

                # Asegurarse de que hay al menos dos valores
                if len(valores) >= 2:
                    try:
                        ch1_fil = int(valores[0])
                        ch1_env = int(valores[1])
                        insertar_dato(ch1_fil, ch1_env)
                        print(f"Registrado CH1_fil: {ch1_fil}, CH1_env: {ch1_env}")
                    except ValueError:
                        print(f"Error al convertir los datos a enteros: {data}")
                else:
                    print(f"Datos incompletos recibidos: {data}")
except serial.SerialException as e:
    print(f"Error al acceder al puerto serial: {e}")
except KeyboardInterrupt:
    print("\nLectura interrumpida. Saliendo...")

# Cerrar la conexión a la base de datos
finally:
    conexion.close()

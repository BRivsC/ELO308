import serial
import sqlite3
import time
from datetime import datetime
import os

# Configurar el puerto serial
puerto_serial = 'COM4'
baud_rate = 115200

# Conectar o crear la base de datos SQLite
db_path = 'registro_datos.db'
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en: {os.path.abspath(db_path)}")

# Crear la tabla si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS datos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    CH1 INTEGER,
                    timestamp INTEGER,  
                    fecha TEXT,
                    gesto TEXT
                )''')

# Inicializamos la variable de tiempo de referencia (start_time)
start_time = None
gesto = input("Por favor, define el gesto para este registro: ")  # Definir gesto al inicio

# Función para insertar datos en la base de datos
def insertar_dato(ch1_valor):
    global start_time
    
    # Si es el primer dato recibido, inicializamos el tiempo de referencia
    if start_time is None:
        start_time = time.time() * 1000  # Milisegundos

    # Calcular milisegundos transcurridos desde el primer dato
    timestamp = int(time.time() * 1000 - start_time)
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("INSERT INTO datos (CH1, timestamp, fecha, gesto) VALUES (?, ?, ?, ?)", 
                   (ch1_valor, timestamp, fecha, gesto))
    conexion.commit()

# Abrir el puerto serial y comenzar a leer datos
try:
    with serial.Serial(puerto_serial, baud_rate, timeout=1) as ser:
        print(f"Leyendo desde {puerto_serial} a {baud_rate} baud...\n")
        while True:
            # Leer línea desde el puerto serial
            if ser.in_waiting > 0:
                data = ser.readline().decode('ascii').rstrip()
                
                # Buscar y extraer el valor de CH1
                if "CH1:" in data:
                    try:
                        ch1_valor = int(data.split("CH1:")[1].strip())
                        insertar_dato(ch1_valor)
                        print(f"Registrado CH1: {ch1_valor}")
                    except ValueError:
                        print(f"Error al convertir el dato a entero: {data}")
except serial.SerialException as e:
    print(f"Error al acceder al puerto serial: {e}")
except KeyboardInterrupt:
    print("\nLectura interrumpida. Saliendo...")

# Cerrar la conexión a la base de datos
finally:
    conexion.close()

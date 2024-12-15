import serial
import sqlite3
import time
from datetime import datetime
import os

# Configurar el puerto serial
puerto_serial = 'COM9'
baud_rate = 115200

# Conectar o crear la base de datos SQLite
db_path = 'datos_validacion_adc_3ch_500SampleFreq.db'
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en: {os.path.abspath(db_path)}")

# Crear la tabla si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS datos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp INTEGER,
                    frec INTEGER,
                    amp FLOAT,
                    CH1 INTEGER,
                    CH2 INTEGER,
                    CH3 INTEGER,
                    placa TEXT
                )''')

# Solicitar la frecuencia, amplitud y nombre de la placa al usuario
frec = int(input("Por favor, ingrese la frecuencia: "))
amp = float(input("Por favor, ingrese la amplitud: "))
placa = input("Por favor, ingrese el nombre de la placa: ")

# Inicializar variables de tiempo
start_time = None  # Tiempo de referencia para calcular el timestamp relativo

# Función para insertar datos en la base de datos
def insertar_dato(frec, amp, ch1, ch2, ch3, placa):
    global start_time
    
    # Si es el primer dato recibido, inicializamos el tiempo de referencia
    if start_time is None:
        start_time = time.time() * 1000  # Milisegundos

    # Calcular milisegundos transcurridos desde el primer dato
    timestamp = int(time.time() * 1000 - start_time)

    cursor.execute("INSERT INTO datos (timestamp, frec, amp, CH1, CH2, CH3, placa) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                   (timestamp, frec, amp, ch1, ch2, ch3, placa))
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

                # Asegurarse de que hay tres valores
                if len(valores) == 3:
                    try:
                        ch1 = int(valores[0])
                        ch2 = int(valores[1])
                        ch3 = int(valores[2])
                        insertar_dato(frec, amp, ch1, ch2, ch3, placa)
                        print(f"Registrado CH1: {ch1}, CH2: {ch2}, CH3: {ch3}")
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

''' Lectura de 3 canales EMG bruto

Script en Python para registrar los datos de EMG recibidos desde el puerto serial
Espera recibirlos con el formato <onset>,<CH1>,<CH2>,<CH3>,...

Estructura de la base de datos:
          id: Identificador único autoincremental para cada entrada
    gesto_id: Identificador único para cada gesto. Útil para diferenciar distintas instancias del mismo gesto
       onset: Indicador de si se está ejecutando el gesto. 1 para indicar que está en ejecución
nombre_gesto: Nombre del gesto hecho
          fs: Frecuencia de muestreo en Hertz
       fecha: Fecha en la que se hizo la captura, YYYY-MM-DD HH:MM:SS
         CHX: Valor recibido para el canal X sin pasar por filtros

Uso: Ejecutar e ingresar nombre del gesto a hacer.
     Mantener pulsado botón en la placa mientras se hace el gesto
     Hacer 1 repetición de 1 gesto por vez!
     Al terminar la toma de datos, finalizar con Ctrl+C y soltar el botón
'''

import serial
import sqlite3
import time
from datetime import datetime
import os

# Configurar el puerto serial
puerto_serial = 'COM3'
baud_rate = 115200

# Frecuencia de muestreo en Hz
fs = 1000

# Conectar o crear la base de datos SQLite
db_path = 'Datos/3ch_gestos_raw.db'
#db_path = 'Datos/3ch_gestos_onsetTest.db'
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en: {os.path.abspath(db_path)}")

# Crear la tabla si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS datos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gesto_id INTEGER,
                    onset INTEGER,
                    nombre_gesto TEXT,
                    fs INTEGER,
                    fecha TEXT,
                    CH1 INTEGER,
                    CH2 INTEGER,
                    CH3 INTEGER
                )''')


# Obtener el último gesto_id registrado en la base de datos
cursor.execute("SELECT MAX(gesto_id) FROM datos")
ultimo_gesto_id = cursor.fetchone()[0]
gesto_id = (ultimo_gesto_id + 1) if ultimo_gesto_id is not None else 1

# Solicitar el gesto_id y el nombre del gesto al usuario
print(f"Último gesto registrado con ID = {gesto_id-1}")
nombre_gesto = input("Por favor, ingrese el nombre del gesto: ")


# Función para insertar datos en la base de datos
# Ingresa lo recibido por consola y lo asocia a gesto, id y fecha
def insertar_dato(gesto_id, nombre_gesto, onset, ch1, ch2, ch3, fs):
    # Obtener fecha
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Insertar en base de datos
    cursor.execute("INSERT INTO datos (gesto_id, nombre_gesto, onset, CH1, CH2, CH3, fecha, fs) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                   (gesto_id, nombre_gesto, onset, ch1, ch2, ch3, fecha, fs))
    conexion.commit()



# Abrir el puerto serial y comenzar a leer datos
try:
    with serial.Serial(puerto_serial, baud_rate, timeout=1) as ser:
        print(f"Leyendo desde {puerto_serial} a {baud_rate} baud...\nFinalizar con Ctrl+C")
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
                            ch1 =   int(valores[1])
                            ch2 =   int(valores[2])
                            ch3 =   int(valores[3])
                            insertar_dato(gesto_id, nombre_gesto, onset, ch1, ch2, ch3, fs)
                            #print(f"Registrado Onset: {onset}\t CH1: {ch1}\t CH2: {ch2}\t CH3: {ch3}")
                        except ValueError:
                            print(f"Error al convertir los datos a enteros: {data}")
                    else:
                        print(f"Datos incompletos recibidos: {data}")
                except UnicodeDecodeError:
                    # Suele caer acá cuando registra datos incompletos desde la consola serial
                    print("Descartada 1ra línea por mala lectura. Reintentando...")
except serial.SerialException as e:
    print(f"Error al acceder al puerto serial: {e}")
except KeyboardInterrupt:
    print(f"\nLectura interrumpida. Datos guardados en {db_path}")

# Cerrar la conexión a la base de datos
finally:
    conexion.close()

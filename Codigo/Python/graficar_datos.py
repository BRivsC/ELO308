import sqlite3
import matplotlib.pyplot as plt
import datetime
import os

# Conectar a la base de datos SQLite
db_path = 'registro_datos_1ch.db'
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en: {os.path.abspath(db_path)}")

# Función para obtener datos de un gesto específico
def obtener_datos_gesto(gesto_id):
    cursor.execute("SELECT timestamp, CH1_fil, CH1_env FROM datos WHERE gesto_id = ?", (gesto_id,))
    datos = cursor.fetchall()
    return datos

# Pedir el gesto_id del gesto a graficar
gesto_id = int(input("Por favor, introduce el gesto_id a graficar: "))

# Obtener los datos del gesto
datos = obtener_datos_gesto(gesto_id)

# Separar los datos en listas para graficar
timestamps = [dato[0] for dato in datos]
CH1_fil_values = [dato[1] for dato in datos]
CH1_env_values = [dato[2] for dato in datos]

# Graficar los datos
plt.figure(figsize=(12, 6))

plt.plot(timestamps, CH1_fil_values, label='CH1 Filtrado', color='blue')
plt.plot(timestamps, CH1_env_values, label='CH1 Envolvente', color='red', linestyle='--')

plt.xlabel('Timestamp (ms)')
plt.ylabel('Valor')
plt.title('Datos de EMG para el gesto con gesto_id = {}'.format(gesto_id))
plt.legend()

# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en: {os.path.abspath(db_path)}")

# Mostrar la gráfica
plt.show()

# Cerrar la conexión a la base de datos
conexion.close()

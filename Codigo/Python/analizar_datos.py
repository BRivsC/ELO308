'''
Script en Python para analizar los datos de sensor EMG capturados.
Al ejecutarlo imprime los gestos disponibles con sus fechas de IDs respectivas.
Pide la ID única de un gesto para graficarlo, obtener su FFT e imprimir por 
consola la SNR y el valor RMS de la señal
'''

import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft
from scipy.signal import welch
import os

# Conectar a la base de datos SQLite
db_path = 'registro_datos_1ch.db'
conexion = sqlite3.connect(db_path)
# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en {os.path.abspath(db_path)}\n")
cursor = conexion.cursor()


# Función para obtener datos de un gesto específico
def obtener_datos_gesto(gesto_id):
    cursor.execute("SELECT timestamp, CH1_fil, CH1_env FROM datos WHERE gesto_id = ?", (gesto_id,))
    datos = cursor.fetchall()
    return datos

# Consultar los datos de gesto_id, fecha y gesto, omitiendo los gesto_id repetidos
cursor.execute("""
    SELECT gesto_id, MIN(fecha), gesto 
    FROM datos 
    GROUP BY gesto_id
""")
datos = cursor.fetchall()

# Imprimir los datos obtenidos por consola
print("---Gestos registrados---")
for fila in datos:
    gesto_id, fecha, gesto = fila
    print(f"Gesto: {gesto}\t Fecha: {fecha}\t ID: {gesto_id}  ")

# Pedir el gesto_id del gesto a graficar
gesto_id = int(input("Por favor, introduce la ID del gesto a graficar: "))

# Obtener los datos del gesto
datos = obtener_datos_gesto(gesto_id)

# Separar los datos en listas para graficar y análisis
timestamps = [dato[0] for dato in datos]
CH1_fil_values = [dato[1] for dato in datos]
CH1_env_values = [dato[2] for dato in datos]

# Calcular la FFT de la señal filtrada
N = len(CH1_fil_values)
T = (timestamps[-1] - timestamps[0]) / N / 1000  # Periodo de muestreo en segundos
yf = fft(CH1_fil_values)
xf = np.linspace(0.0, 1.0/(2.0*T), N//2)

# Calcular la SNR
f, Pxx = welch(CH1_fil_values, fs=1/T, nperseg=1024)
signal_power = np.mean(Pxx)
noise_power = np.mean(Pxx[f > 60])  # Consideramos ruido todo por encima de 60 Hz
snr = 10 * np.log10(signal_power / noise_power)
# Justificar!


# Calcular el valor RMS
rms = np.sqrt(np.mean(np.square(CH1_fil_values)))

# Graficar los datos
#fig, axs = plt.subplots(2, 1, figsize=(12, 18))
fig, axs = plt.subplots(2, 1)

# Gráfico de señal en el dominio del tiempo
axs[0].plot(timestamps, CH1_fil_values, label='CH1 Filtrado', color='blue')
axs[0].plot(timestamps, CH1_env_values, label='CH1 Envolvente', color='red', linestyle='--')
axs[0].set_xlabel('Timestamp [ms]')
axs[0].set_ylabel('Valor [V]')
axs[0].set_title('Datos de EMG para el gesto "{}" (ID:{})'.format(gesto,gesto_id))
axs[0].legend()

# Gráfico de la FFT
axs[1].plot(xf, 2.0/N * np.abs(yf[:N//2]), label='FFT de CH1 Filtrado')
axs[1].set_xlabel('Frecuencia [Hz]')
axs[1].set_ylabel('Amplitud')
axs[1].set_title('Transformada Rápida de Fourier (FFT)')
axs[1].legend()

# Mostrar SNR y RMS en consola
print(f"SNR: {snr:.2f} dB")
print(f"Valor RMS: {rms:.2f}")

# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en: {os.path.abspath(db_path)}")

# Guardar el plot creado
plt.tight_layout()
directorio = 'fig_1ch'
if not os.path.exists(directorio):
    os.makedirs(directorio)
ruta_archivo = os.path.join(directorio, 'grafico.png')
nombre_archivo = f"{gesto}_{gesto_id}.png"
ruta_archivo = os.path.join(directorio, nombre_archivo)
plt.savefig(ruta_archivo)
#plt.savefig('/fig_1ch/{}_{}.png'.format(gesto,gesto_id))
print(f"Guardando gráfico en {ruta_archivo}\n")

# Mostrar la gráfica
plt.show()


# Cerrar la conexión a la base de datos
conexion.close()

import sqlite3
from scipy.fftpack import fft
import os
import matplotlib.pyplot as plt
import numpy as np

def graficar_fft(gesto_id, ruta_db = 'Datos/datos_gestos_3ch.db', tabla_fft = 'fft'):
    # Graficar
    # Cargar desde la tabla con fft
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()
    cursor.execute(f"""
        SELECT ch1_fft, ch2_fft, ch3_fft, fs, nombre_gesto
        FROM {tabla_fft} 
        WHERE gesto_id = ?
    """,(gesto_id,))
    datos_graficar = cursor.fetchall() # Formato: [ch1_fft, ch2_fft, ch3_fft, fs]

    fs = datos_graficar[0][-2]
    nombre = datos_graficar[0][-1]
    ch1_fft = [dato[0] for dato in datos_graficar] 
    #ch2_fft = [dato[1] for dato in datos_graficar] 
    #ch3_fft = [dato[2] for dato in datos_graficar] 
    # Crear la figura y los subplots

    
    # Generar el vector de tiempo
    N = len(ch1_fft)
    T = 1.0 / fs  # Periodo de muestreo en segundos
    #xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    xf = np.linspace(0.0, 1.0/(2.0*T), N)
    
    # Graficar
    plt.plot(xf, ch1_fft, color='b', label=f'{nombre}')
    plt.suptitle(f'FFT de {nombre}')
    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Magnitud [dB]')
    plt.show()



graficar_fft(2, ruta_db = 'Datos/datos_gestos_3ch.db', tabla_fft = 'fft')
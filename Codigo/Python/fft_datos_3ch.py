import sqlite3
import matplotlib.pyplot as plt
import matplotlib as mpl  
import numpy as np
from scipy.fftpack import fft
import os

# Conectar a la base de datos SQLite
db_path = 'Datos/datos_gestos_3ch.db'
nombre_tabla = 'raw'
# Factor de reescalado. En este caso se usa un ADC de 10 bits con 5 volts máx.
reescalado = 5.0/1023 
conexion = sqlite3.connect(db_path)
# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en {os.path.abspath(db_path)}\n")
cursor = conexion.cursor()



# Consultar los datos de gesto_id, fecha y gesto, omitiendo gesto_id repetidos
cursor.execute(f"""
    SELECT gesto_id, MIN(fecha), nombre_gesto 
    FROM {nombre_tabla} 
    GROUP BY gesto_id
""")
datos = cursor.fetchall()

# Imprimir los datos obtenidos por consola
print("---Gestos registrados---")
for fila in datos:
    gesto_id, fecha, gesto = fila
    print(f"ID: {gesto_id}    \tFecha: {fecha}\tGesto: {gesto}")

# Pedir el gesto_id del gesto a graficar
gesto_id = int(input("Por favor, introduce la ID del gesto a graficar: "))


# Obtener los datos del gesto
nombre_tabla = 'raw' 

cursor.execute(f"""SELECT fs, onset, abs(CH1) * {reescalado},
               abs(CH2) * {reescalado}, abs(CH3) *{reescalado}, nombre_gesto 
            FROM {nombre_tabla} 
            WHERE gesto_id = ?
            AND onset = 1"""
            , (gesto_id,))
datos = cursor.fetchall()
nombre_gesto = datos[0][-1]  # Obtener el nombre del gesto


# Separar los datos en listas para graficar y análisis, filtrando por onset = 1
fs = datos[0][0]  # La frecuencia de muestreo es igual para todos los datos

CH1_values = [dato[2] for dato in datos if dato[1] == 1]
CH2_values = [dato[3] for dato in datos if dato[1] == 1]
CH3_values = [dato[4] for dato in datos if dato[1] == 1]

# Generar el vector de tiempo
N = len(CH1_values)
T = 1.0 / fs  # Periodo de muestreo en segundos
time_vector = np.linspace(0.0, N * T, N)

# Eliminar la componente de DC (valor medio)
CH1_values = CH1_values - np.mean(CH1_values)
CH2_values = CH2_values - np.mean(CH2_values)
CH3_values = CH3_values - np.mean(CH3_values)



# Calcular la FFT de las señales filtradas
yf_CH1 = fft(CH1_values)
yf_CH2 = fft(CH2_values)
yf_CH3 = fft(CH3_values)
xf = np.linspace(0.0, 1.0 / (2.0 * T), N // 2)

# Graficar los datos
mpl.rc('font',family='Times New Roman')
fig, axs = plt.subplots(3, 1, figsize=(2, 2))

# Límites eje Y
yinf = 0
ysup = 0.1

# Tamaños de fuente
titulo_size = 12
tick_size = 8
label_size = 10

# Ticks de ejes
yticks = [0, 0.05, 0.1]
xticks = [0, 200, 400]

# Gráficos de la FFT
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, 
                    hspace=None)
axs[0].plot(xf, 2.0 / N * np.abs(yf_CH1[:N // 2]), label='FFT de CH1')
axs[0].set_ylabel('CH1', fontsize = label_size)
axs[0].set_ylim(yinf, ysup)
axs[0].set_title(f'FFT de {nombre_gesto}', fontsize = titulo_size)  
axs[0].tick_params(labelbottom=False) # Omite los números del eje X
axs[0].set_xticks(xticks) 
axs[0].set_yticks(yticks) 
axs[0].grid()

axs[1].plot(xf, 2.0 / N * np.abs(yf_CH2[:N // 2]), label='FFT de CH2')
axs[1].set_ylabel('CH2', fontsize = label_size)
axs[1].set_ylim(yinf, ysup)
axs[1].tick_params(labelbottom=False) # Omite los números del eje X
axs[1].set_xticks(xticks) 
axs[1].set_yticks(yticks) 
axs[1].grid()

axs[2].plot(xf, 2.0 / N * np.abs(yf_CH3[:N // 2]), label='FFT de CH3')
axs[2].set_ylabel('CH3', fontsize = label_size)
axs[2].set_ylim(yinf, ysup)
axs[2].set_xlabel('Frecuencia [Hz]', fontsize = label_size)
axs[2].set_xticks(xticks) 
axs[2].set_yticks(yticks) 
axs[2].grid()
plt.tight_layout()
fig.subplots_adjust(hspace=0.5, left=0.35)

# Guardar gráfico generado
directorio = 'fig_3ch/fft'
if not os.path.exists(directorio):
    os.makedirs(directorio)
nombre_archivo = f"{gesto_id}_{nombre_gesto}.png"
ruta_archivo = os.path.join(directorio, nombre_archivo)
plt.savefig(ruta_archivo)
print(f"Guardando gráfico en {ruta_archivo}")
#plt.show()


# Cerrar la conexión a la base de datos
conexion.close()

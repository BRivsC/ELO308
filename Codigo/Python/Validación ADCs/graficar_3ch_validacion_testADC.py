import sqlite3
import matplotlib.pyplot as plt
import matplotlib as mpl  
import numpy as np

mpl.rc('font',family='Times New Roman')
### Solicitar los valores al usuario ###
sample_rate = int(input("Ingresa la frecuencia de muestreo [500|1000]: "))
if sample_rate == 500:
    db_path = 'datos_validacion_adc_3ch_500SampleFreq.db'
else:
    db_path = 'datos_validacion_adc_3ch_1000SampleFreq.db'

frec = int(input("Ingresa la frecuencia de la señal [50|100|150]: "))
amp = 0.3
placa = input("Elige una placa \n1:Arduino Nano\n2:ESP32\n> ")
if placa == "1":
    placa = "Arduino Nano"
else:
    placa = "ESP32"

### Base de datos ###
# Conectar a la base de datos SQLite
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Consultar los datos de timestamp, CH1, CH2 y CH3 que coincidan con la frecuencia, amplitud y placa especificados
cursor.execute("SELECT timestamp, CH1, CH2, CH3 FROM datos WHERE frec = ? AND amp = ? AND placa = ?", (frec, amp, placa))
datos = cursor.fetchall()

# Separar los datos en listas individuales
timestamps = [fila[0]/3.5 for fila in datos]  # dividido por 2 para compensar unos temas con la frecuencia
# Ajuste de voltaje a bits de ADC
if placa == "ESP32":
    # ESP32: Resolución de 12 bits, llega hasta 4095 con 3.3 V
    factorCorreccion = (4095/3.3)

else:
    # Arduino Nano: Resolución de 10 bits, llega hasta 1023 con 5 V
    factorCorreccion = (1023/5)

CH1 = [fila[1]/factorCorreccion for fila in datos]
CH2 = [fila[2]/factorCorreccion for fila in datos]
CH3 = [fila[3]/factorCorreccion for fila in datos]

### Límites de gráficos ###
# Tiempo (en ms) para graficar
xinf = 0
xsup = 150

# Rangos de voltajes
yinf = 1.4 # Volts
ysup = 2.2 # Volts

# Autoajustar rangos según resolución de ADC para graficar
#yinf = int(yinf * factorCorreccion )
#ysup = int(ysup * factorCorreccion )


### Señal de referencia ###
amplitud = 0.13     # Volts, AC
#offset = 1.9        # Volts, DC  ard=1.9 esp=1.7

if placa == "ESP32":
    offset = 1.65
else:
    offset = 1.9
    
frec_ref = frec # Hz
fase = np.pi/4         # Radianes


# Vector de tiempo de la sinusoidal
time_ref = np.array(range(xinf,xsup)) # en ms
referencia = (amplitud * np.sin(2 * np.pi * frec_ref * time_ref/1000 + fase)) + offset


### Graficar ###
# Crear subplots y cambiar fuente
fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)


# Título general
fig.suptitle(f'Lecturas con señal de {amp} Vpp @ {frec} Hz con placa {placa}.\nMuestreo a {sample_rate} Hz', fontsize=20)

# Graficar CH1 y la referencia
axs[0].plot(timestamps, CH1, label='CH1', color='blue')
axs[0].plot(time_ref, referencia, label='Referencia', color='black', linestyle='--', linewidth=1)
axs[0].set_ylabel('ADC CH1 (V)', fontsize=18)
axs[0].grid(True)
axs[0].tick_params(axis='y', labelsize=18)
axs[0].set_ylim(yinf, ysup)

# Graficar CH2 y la referencia
axs[1].plot(timestamps, CH2, label='CH2', color='green')
axs[1].plot(time_ref, referencia, label='Referencia', color='black', linestyle='--', linewidth=1)
axs[1].set_ylabel('ADC CH2 (V)', fontsize=18)
axs[1].grid(True)
axs[1].tick_params(axis='y', labelsize=18)
axs[1].set_ylim(yinf, ysup)

# Graficar CH3 y la referencia
axs[2].plot(timestamps, CH3, label='CH3', color='red')
axs[2].plot(time_ref, referencia, label='Referencia', color='black', linestyle='--', linewidth=1)
axs[2].set_ylabel('ADC CH3 (V)', fontsize=18)
axs[2].set_xlabel('Tiempo (ms)', fontsize=18)
axs[2].grid(True)
axs[2].tick_params(axis='y', labelsize=18)
axs[2].tick_params(axis='x', labelsize=18)
axs[2].set_ylim(yinf, ysup)

# Añadir leyendas a cada subplot
for ax in axs:
    ax.legend(loc = "upper right",fontsize=18)

# Ajustar el layout
plt.tight_layout()

# Ajustar espacios
plt.xlim(xinf, xsup)
#plt.ylim(1900,2300)
plt.subplots_adjust(right=0.95, bottom=0.15)

# Guardar gráfico
plt.savefig(f"Plots/{placa} {amp}Vpp {frec}Hz sample{sample_rate}.png")
print(f"Guardado gráfico en 'Plots/{placa}_{amp}Vpp_{frec}Hz_sample{sample_rate}.png'")

# Mostrar el gráfico
plt.show()

# Cerrar la conexión a la base de datos
conexion.close()

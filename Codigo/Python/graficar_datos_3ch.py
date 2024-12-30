''' Graficar datos

Script en Python para visualizar los datos de sensor EMG capturados.
Al ejecutarlo imprime los gestos disponibles con sus fechas de IDs respectivas.
Pide la ID única de un gesto para graficarlo

Bastián Rivas
'''

import sqlite3
import matplotlib.pyplot as plt
import matplotlib as mpl  
import numpy as np
import os

# Conectar a la base de datos SQLite
db_path = 'Datos/datos_gestos_3ch.db'
nombre_tabla = 'raw'
conexion = sqlite3.connect(db_path)
reescalado = 5.0/1023
# Mostrar la ubicación de la base de datos en consola
print(f"Usando base de datos en {os.path.abspath(db_path)}\n")
cursor = conexion.cursor()


# Consultar los datos de gesto_id, fecha y gesto, omitiendo gesto_id repetidos
cursor.execute(f"""
    SELECT gesto_id, MIN(fecha), sesion_id, nombre_gesto
    FROM {nombre_tabla} 
    GROUP BY gesto_id
""")
datos = cursor.fetchall()

# Mostrar todos los gestos registrados en la base de datos
print(f"""--- Gestos registrados ---
ID  \tFecha              \tSesión\tNombre del gesto
----\t-------------------\t------\t----------------
""")

for fila in datos:
    gesto_id, fecha, sesion_id, nombre_gesto = fila
    print(f"{gesto_id}\t{fecha}\t{sesion_id}\t{nombre_gesto}")


# Obtener el gesto_id con la mayor ID por defecto 
cursor.execute(f"SELECT MAX(gesto_id) FROM {nombre_tabla}") 
max_gesto_id = cursor.fetchone()[0]

# Pedir el gesto_id del gesto a graficar 
gesto_id_input = input(f"Por favor, introduce la ID del gesto a graficar 
                       (Enter para usar el más nuevo): ") 

# Usar el gesto_id ingresado o el mayor ID por defecto 
gesto_id = int(gesto_id_input) if gesto_id_input else max_gesto_id

#for gesto_id in range(106,124):
if gesto_id:

    # Obtener los datos del gesto
    cursor.execute(f"""SELECT fs, onset, CH1 * {reescalado}, CH2 * {reescalado},
                   CH3 * {reescalado}, nombre_gesto 
                FROM {nombre_tabla} 
                WHERE gesto_id = ?""", 
                (gesto_id,))

    datos = cursor.fetchall()
    nombre_gesto = datos[0][-1]  # Obtener el nombre del gesto

    # Separar los datos en listas para graficar y análisis
    fs = datos[0][0]  # La frecuencia de muestreo es igual para todos los datos
    onset_values = [dato[1] for dato in datos]

    # Lista de valores por canal
    CH1_values = [dato[2] for dato in datos]
    CH2_values = [dato[3] for dato in datos]
    CH3_values = [dato[4] for dato in datos]


    # Generar el vector de tiempo
    N = len(CH1_values)
    T = 1.0 / fs  # Periodo de muestreo en segundos
    time_vector = np.linspace(0.0, N*T, N)

    # Encontrar los puntos de cambio en el onset
    onset_changes = [i for i in range(1, len(onset_values)) 
                     if onset_values[i] != onset_values[i-1]]

    
    # Tamaños de fuente
    titulo_size = 12
    tick_size = 8
    label_size = 10

    # Graficar los datos
    mpl.rc('font',family='Times New Roman')
    fig, axs = plt.subplots(3, 1, figsize=(2, 2.5)) 
    fig.suptitle(f'Señal bruta de\n{nombre_gesto}', fontsize = titulo_size)
    plt.subplots_adjust(left = 0.25, right=0.95, bottom=0.19, top = 0.85)

    # Límites eje Y
    yinf = -0.3
    ysup = 3.3

    # Graficar CH1
    axs[0].plot(time_vector, CH1_values, label='CH1')
    axs[0].set_ylabel('CH1[V]', fontsize = label_size)
    axs[0].set_ylim(yinf, ysup)
    axs[0].tick_params(labelbottom=False) # Omite los números del eje X
    axs[0].grid()
    for change in onset_changes:
        axs[0].axvline(x=time_vector[change], color='red', linestyle='--')

    # Graficar CH2
    axs[1].plot(time_vector, CH2_values, label='CH2')
    axs[1].set_ylabel('CH2[V]', fontsize = label_size)
    axs[1].set_ylim(yinf, ysup)
    axs[1].tick_params(labelbottom=False) # Omite los números del eje X
    axs[1].grid()
    for change in onset_changes:
        axs[1].axvline(x=time_vector[change], color='red', linestyle='--')

    # Graficar CH3
    axs[2].plot(time_vector, CH3_values, label='CH3')
    axs[2].set_ylabel('CH3[V]', fontsize = label_size)
    axs[2].set_xlabel('Tiempo [s]', fontsize = label_size)
    axs[2].set_ylim(yinf, ysup)
    axs[2].grid()
    for change in onset_changes:
        axs[2].axvline(x=time_vector[change], color='red', linestyle='--')

    # Ajustar el layout
    #plt.tight_layout()

    # Guardar gráfico generado
    directorio = 'fig_3ch/raw'
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    nombre_archivo = f"{gesto_id}_{nombre_gesto}.png"
    ruta_archivo = os.path.join(directorio, nombre_archivo)
    plt.savefig(ruta_archivo)
    print(f"Guardando gráfico en {ruta_archivo}")

# Mostrar la gráfica
#plt.show()


# Cerrar la conexión a la base de datos
conexion.close()

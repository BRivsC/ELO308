""" FFT de gestos
Script para guardar en una nueva tabla las FFT de los gestos. Incluye funciones para calcular la FFT, RMS, y SNR de los gestos,
como también un ejemplo en el que se calcula con todas las entradas de una tabla.

    Estructura de la base de datos
    ------------------------------
        gesto_id (int)       : Identificador único para cada gesto. Útil para diferenciar distintas instancias del mismo gesto
        sesion_id (int)      : ID de la sesión en la que se hizo la captura
        nombre_gesto (string): Nombre del gesto hecho
        fecha (string)       : Fecha en la que se hizo la captura, YYYY-MM-DD HH:MM:SS
        fs (int)             : Frecuencia de muestreo en Hertz
        fc (int)             : Frecuencia de corte del filtro 
        chX_fft (float)      : FFT de la señal en el canal X
        chX_rms_senal (float): RMS de la señal en el canal X
        chX_rms_ruido (float): RMS del ruido en el canal X
        chX_SNR (float)      : SNR del canal X
        

Bastián Rivas
"""
import sqlite3
from scipy.fftpack import fft
import os
import matplotlib.pyplot as plt


#%% Función para calcular RMS
import numpy as np
def get_rms(values):
    """
    Calcula el valor RMS de una lista de valores.

    Parameters
    ----------
        values (list or np.array): Lista de valores numéricos.

    Return
    ------
        float: El valor RMS de la lista.
    """
    values = np.array(values)
    rms = np.sqrt(np.mean(np.square(values)))
    return rms

#%% Función para calcular la SNR
import numpy as np

def get_SNR(signal_rms, noise_rms):
    """
    Calcula la relación señal a ruido (SNR) a partir de los valores RMS de la señal y del ruido.

    Parameters
    ----------
        signal_rms (float): El valor RMS de la señal.
        noise_rms (float): El valor RMS del ruido.

    Return
    ------
        float: El valor de la SNR en decibeles (dB).
    """
    snr = 20 * np.log10(signal_rms / noise_rms)
    return snr

#%%

def calcular_fft_snr(gesto_id, ruta_db = 'Datos/datos_gestos_3ch.db', 
                     tabla_norm = 'norm', fs = 1000, fc = 150, 
                     canales = [1, 2, 3]):
    """
    Script para calcular la FFT de hasta tres canales de un gesto específico a 
    partir de su ID, almacenado en una base de datos en SQLite.
    Requiere que en la base de datos existan hasta 3 canales de registros del 
    gesto a usar y un registro llamado 'Reposo' correspondiente a la sesión en 
    la que se capturaron los datos
    Ojo: retorna el lado derecho de la FFT (aka:mlas frecuencias positivas)

    Parameters
    ----------
    - "gesto_id": Número identificador del gesto a normalizar
    - "ruta_db": La ruta a la base de datos SQLite que por defecto es 
    'Datos/datos_gestos_3ch.db'.
    - "tabla_norm": El nombre de la tabla dentro de la base de datos donde se 
    registran los datos previamente filtrados
    - "fs": La frecuencia de muestreo, cuyo valor por defecto es 1000 Hz.
    - "fc": La frecuencia de corte para el filtrado, cuyo valor por defecto es 
    150 Hz.
    - "canales": Lista de canales a analizar, que por defecto es [1, 2, 3]


    Este script realiza las siguientes operaciones:
    1. Conectar a la base de datos SQLite especificada.
    2. Obtener los datos de la señal para el "gesto_id" proporcionado.
    3. Filtrar las señales con la frecuencia y el orden especificado
    4. Calcular las envolventes de los 3 canales
    5. Normalizar las señales a partir de su contracción voluntaria máxima (CVM)

    
    Return
    ------
        datos_fft: array_like
            Un diccionario con las siguientes entradas:
               - gesto_id (int)       : Identificador único para cada gesto. Útil para diferenciar distintas instancias del mismo gesto
               - sesion_id (int)      : ID de la sesión en la que se hizo la captura
               - nombre_gesto (string): Nombre del gesto hecho
               - fecha (string)       : Fecha en la que se hizo la captura, YYYY-MM-DD HH:MM:SS
               - fs (int)             : Frecuencia de muestreo en Hertz
               - fc (int)             : Frecuencia de corte del filtro 
               - ch1_fft (float)      : FFT de la señal en el canal 1
               - ch1_rms_senal (float): RMS de la señal en el canal 1
               - ch1_rms_ruido (float): RMS del ruido en el canal 1
               - ch1_SNR (float)      : SNR del canal 1
               - ch2_fft (float)      : FFT de la señal en el canal 2
               - ch2_rms_senal (float): RMS de la señal en el canal 2
               - ch2_rms_ruido (float): RMS del ruido en el canal 2
               - ch2_SNR (float)      : SNR del canal 2
               - ch3_fft (float)      : FFT de la señal en el canal 3
               - ch3_rms_senal (float): RMS de la señal en el canal 3
               - ch3_rms_ruido (float): RMS del ruido en el canal 3
               - ch3_SNR (float)      : SNR del canal 3



"""
    ### Nuevo: Calcular RMS y SNR de las señales
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()

    # Obtener valores de la señal funcional. De acá interesan los valores cuyo onset sea 1, fs, fc, fecha y su nombre
    cursor.execute(f"""
            SELECT sesion_id, fecha, fs, fc, ch1_env_fil, ch2_env_fil, ch3_env_fil, nombre_gesto
            FROM {tabla_norm} 
            WHERE gesto_id = ?
            AND onset = 1
        """,(gesto_id,))
    datos = cursor.fetchall()

    # Formato: [sesion_id, fs, fc, ch1_env_fil, ch2_env_fil, ch3_env_fil, nombre_gesto]

    # Diccionario para ir registrando los datos que corresponden a cada canal
    canales = [1, 2, 3]
    emg_env_fil = {1: [],2: [],3: []}
    for num_canal in canales:
        # emg_env_fil[i] corresponde al canal i
        emg_env_fil[num_canal] = [dato[3 + num_canal] for dato in datos] 

    # Estos datos son los mismos para los 3 canales a través de todo el tiempo
    sesion_id_gesto = datos[0][0]
    fecha_gesto = datos [0][1]
    fs = datos[0][2] 
    fc = datos[0][3] 
    nombre_gesto_funcional = datos[0][-1] 

    # Obtener los registros de ruido (Reposo) correspondientes a la sesión
    cursor.execute(f"""
        SELECT ch1_env_fil, ch2_env_fil, ch3_env_fil
        FROM {tabla_norm} 
        WHERE nombre_gesto LIKE '%Reposo%'
        AND sesion_id = ?
    """,(sesion_id_gesto,))

    datos = cursor.fetchall() 
    
    ruido_env_fil = {1: [],2: [],3: []}
    rms_senal = {1: [],2: [],3: []}
    rms_ruido = {1: [],2: [],3: []}
    SNR = {1: [],2: [],3: []}
    fft_emg = {1: [],2: [],3: []}
    fft_emg_magnitude = {1: [],2: [],3: []}
    
    for num_canal in canales:
        # ruido_env_fil[i] corresponde al canal i
        ruido_env_fil[num_canal] = [dato[num_canal - 1] for dato in datos] 
    
        # Calcular RMS de gesto y de ruido
        rms_senal[num_canal] = get_rms(emg_env_fil[num_canal]) # RMS del gesto postprocesado
        rms_ruido[num_canal] = get_rms(ruido_env_fil[num_canal])    # RMS del ruido postprocesado

        # Obtener SNR con SNR = 20 * log10(RMS_Señal / RMS_Ruido)
        SNR[num_canal] = get_SNR(rms_senal[num_canal], rms_ruido[num_canal])

        ### Obtener FFT de la señal
        fft_emg[num_canal] = fft(emg_env_fil[num_canal])

        # Obtener el lado derecho de la FFT
        N = len(fft_emg[num_canal])
        fft_emg_magnitude[num_canal] = 2.0 / N * np.abs(fft_emg[num_canal][:N//2])

        # Convertir a dB
        fft_emg_magnitude[num_canal] = 20 * np.log10(fft_emg_magnitude[num_canal])


        # Valores a retornar:
        resultado_fft = {
        'gesto_id': gesto_id,
        'sesion_id': sesion_id_gesto,
        'nombre_gesto': nombre_gesto_funcional,
        'fecha': fecha_gesto,
        'fs': fs,
        'fc': fc,
        # Canal 1
        'ch1_fft'       : fft_emg_magnitude[1], # FFT de la señal en dB
        'ch1_rms_senal' : rms_senal[1],         # RMS de la señal del gesto
        'ch1_rms_ruido' : rms_ruido[1],         # RMS del ruido del canal
        'ch1_SNR'       : SNR[1],               # SNR obtenido a partir del RMS 
        # Canal 2
        'ch2_fft'       : fft_emg_magnitude[2], # FFT de la señal en dB
        'ch2_rms_senal' : rms_senal[2],         # RMS de la señal del gesto
        'ch2_rms_ruido' : rms_ruido[2],         # RMS del ruido del canal
        'ch2_SNR'       : SNR[2],               # SNR obtenido a partir del RMS 
        # Canal 3
        'ch3_fft'       : fft_emg_magnitude[3], # FFT de la señal en dB
        'ch3_rms_senal' : rms_senal[3],         # RMS de la señal del gesto
        'ch3_rms_ruido' : rms_ruido[3],         # RMS del ruido del canal
        'ch3_SNR'       : SNR[3],               # SNR obtenido a partir del RMS 
    }

    return resultado_fft

#%%

def registrar_datos_fft(datos_fft, ruta_db='Datos/datos_gestos_3ch.db', 
                        tabla_fft = 'fft', tabla_norm = 'norm'):
    """
    Registra las FFT calculadas, RMS y SNR en la base de datos.

    
    Parameters
    ----------
    - "datos_fft": Datos correspondiente a 1 gesto
    - "ruta_db": La ruta a la base de datos SQLite que por defecto es 
                 'Datos/datos_gestos_3ch.db'.
    - "tabla_fft": El nombre de la tabla dentro de la base de datos donde se 
                   registran los resultados de la FFT
    - "tabla_norm": El nombre de la tabla dentro de la base de datos con los 
                    datos normalizados

    Estructura de la base de datos
    ------------------------------
        gesto_id (int)       : Identificador único para cada gesto. Útil para 
                               diferenciar distintas instancias del mismo gesto
        sesion_id (int)      : ID de la sesión en la que se hizo la captura
        nombre_gesto (string): Nombre del gesto hecho
        fecha (string)       : Fecha en la que se hizo la captura, 
                               YYYY-MM-DD HH:MM:SS
        fs (int)             : Frecuencia de muestreo en Hertz
        fc (int)             : Frecuencia de corte del filtro 
        chX_fft (float)      : FFT de la señal en el canal X
        chX_rms_senal (float): RMS de la señal en el canal X
        chX_rms_ruido (float): RMS del ruido en el canal X
        chX_SNR (float)      : SNR del canal X

    """
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()

    # Crear la tabla "fft" y ejecutar la consulta para crearla
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {tabla_fft} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gesto_id INTEGER,
        sesion_id INTEGER,
        nombre_gesto TEXT,
        fecha TEXT,
        fs INTEGER,
        fc INTEGER,
        ch1_fft REAL,
        ch1_rms_ruido REAL,
        ch1_rms_senal REAL,
        ch1_SNR REAL,
        ch2_fft REAL,
        ch2_rms_ruido REAL,
        ch2_rms_senal REAL,
        ch2_SNR REAL,
        ch3_fft REAL,
        ch3_rms_ruido REAL,
        ch3_rms_senal REAL,
        ch3_SNR REAL

    );
    """)


    # Anotar todos los registros correspondientes al gesto especificado
    # Los 3 canales tienen el mismo largo así que se puede usar cualquiera
    n_registros = len(datos_fft['ch1_fft']) 

    
    for i in range(n_registros):
        insertar_query = f"""
       INSERT INTO {tabla_fft}(gesto_id, sesion_id, nombre_gesto, fecha, fs, fc, 
                                 ch1_fft, ch1_rms_ruido, ch1_rms_senal, ch1_SNR, 
                                 ch2_fft, ch2_rms_ruido, ch2_rms_senal, ch2_SNR, 
                                 ch3_fft, ch3_rms_ruido, ch3_rms_senal, ch3_SNR)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        valores = (
            datos_fft['gesto_id'],
            datos_fft['sesion_id'],
            datos_fft['nombre_gesto'],
            datos_fft['fecha'],
            datos_fft['fs'],
            datos_fft['fc'],
            datos_fft['ch1_fft'][i],
            datos_fft['ch1_rms_ruido'],
            datos_fft['ch1_rms_senal'],
            datos_fft['ch1_SNR'],
            datos_fft['ch2_fft'][i],
            datos_fft['ch2_rms_ruido'],
            datos_fft['ch2_rms_senal'],
            datos_fft['ch2_SNR'],
            datos_fft['ch3_fft'][i],
            datos_fft['ch3_rms_ruido'],
            datos_fft['ch3_rms_senal'],
            datos_fft['ch3_SNR'],

        )
        cursor.execute(insertar_query, valores)

    
    conexion.commit()
    conexion.close()

    print(f"Registrado '{datos_fft['nombre_gesto']}' con ID 
          {datos_fft['gesto_id']} en la tabla '{tabla_norm}'.")


#%% 
if __name__ == '__main__':
    '''
    Generar una tabla con la FFT de TODOS los datos normailzados registrados en 
    tabla_norm.
    Se appoya en las funciones de registrar_datos_fft y calcular_fft_snr.
    También sirve como ejemplo de uso para las funciones anteriormente 
    mencionadas
    '''
    ruta_db = '3ch_gestos_testing.db'
    tabla_norm = 'norm'
    tabla_fft = 'fft'
  

    # Conectarse a la base de datos
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()


    # Mostrar la ubicación de la base de datos en consola
    print(f"Usando base de datos en: {os.path.abspath(ruta_db)}")
    print(f"Los gestos normalizados se leerán en la tabla '{tabla_norm}' y las 
            FFT se guardarán en '{tabla_fft}'")

    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()

    # Inicio de interacción con usuario
    # Mostrar los gestos almacenados en la tabla de los normalizados
    cursor.execute(f"""
        SELECT gesto_id, MIN(fecha), nombre_gesto, sesion_id 
        FROM {tabla_norm} 
        GROUP BY gesto_id
    """)
    datos = cursor.fetchall()

    print(f"""--- Gestos registrados ---
ID  \tFecha              \tSesión\tNombre del gesto
----\t-------------------\t------\t----------------""")
    gestos_a_procesar = []
    for fila in datos:
        gesto_id, fecha, gesto, sesion_id = fila
        print(f"{gesto_id}\t{fecha}\t{sesion_id}\t{gesto}")
        gestos_a_procesar.append(gesto_id)
    
    n_gestos = len(gestos_a_procesar)
    rpta = []
    
    # Confirmación porque puede tomar un rato
    while rpta not in ["y", "n"]:
        rpta = input(f"¿Calcular la FFT de los {n_gestos} gestos? 
                     [Y/n]: ").lower()

    # Empezar con procesamiento si se recibió una Y
    if rpta == "n":
        print("Cancelando...")
        quit()
    else:
        for gesto in gestos_a_procesar:
            # Obtener FFT de todos los gestos
            datos_fft = calcular_fft_snr(gesto, ruta_db, tabla_norm)
            registrar_datos_fft(datos_fft, ruta_db, 'fft')
            
    
    print(f"Finalizado. {n_gestos} gestos registrados.")

    conexion.close()


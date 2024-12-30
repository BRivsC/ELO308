# -*- coding: utf-8 -*-

"""Ajustando una señal electromiográfica funcional:

-Laboratorio Integrativo de Biomecánica y Fisiología del Esfuerzo,
Escuela de Kinesiología, Universidad de los Andes, Chile-
-Escuela de Ingeniería Biomédica, Universidad de Valparaíso, Chile-
        --Profesores: Oscar Valencia & Alejandro Weinstein--

        
Modificado por Bastián Rivas para ser usado en el trabajo "Caracterización de 
sensores EMG en gestos de mano"
Incluye una serie de funciones nuevas para trabajar con una base de datos en 
SQLite y algunos ajustes para seguir con la línea del trabajo


Todos los créditos van a sus respectivos autores

Changelog:
18-12:
    - Modificado el ejemplo para usar SQLite en lugar de csv
    - Reescalado el gráfico generado para facilitar su lectura desde un 
    documento impreso
    - Agregada interacción con el script por medio de consola
20-12:
    - Calcular SNR de una señal
    - Calcular FFT de una señal
    - Generar una nueva ventana para mostrar lo nuevo
21-12:
    - Automatizada la elección de CVM y ruido en base a sesión

22-12:
    - Automatizado todo el procesamiento por cada gesto y canal
    - Movidos los cálculos de fft a 'generar_tabla_fft_gestos.py' para mantener 
    modularidad
24-12:
    - Agregado un ejemplo con el que se grafica a partir de la base de datos
"""
# Importar librerias
import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt

# Nuevo: para trabajar con sqlite
import sqlite3
import os

# Nuevo: para cambiar el tipo de fuente de los gráficos
import matplotlib as mpl


def ajusta_emg_func(emg_fun, emg_cvm, fs, fc, forden):
    """Ajusta EMG funcional según contracción voluntaria máxima.

    La función utiliza una señal EMG funcional y otra basada en la
    solicitación de una contracción isométrica voluntaria máxima. Ambas señales
    son procesadas considerando su centralización (eliminación de
    "offset"), rectificación y filtrado (pasa bajo con filtfilt).

    Parameters
    ----------
    emg_fun : array_like
        EMG funcional del músculo a evaluar
    emg_cvm : array_like
        EMG vinculada a la contracción voluntaria máxima del mismo músculo
    fs : float
       Frecuencia de muestreo, en hertz, de la señal EMG. Debe ser la misma
       para ambas señales.
    fc : float
        Frecuencia de corte, en hertz, del filtro pasa-bajos.
    forden : int
        Orden del filtro pasa bajos

    Return
    ------
    emg_fun_norm : array_like
        EMG funcional filtrada y  normalizada
    emg_fun_env_f : array_like
        Envolvente de EMG funcional filtrada
    emg_cvm_envf_ : array_like
        Envolvente de EMG CVM filtrada
    """
    #centralizando y rectificando las señales EMG
    emg_fun_env = abs(emg_fun - np.mean(emg_fun))
    emg_cvm_env = abs(emg_cvm - np.mean(emg_cvm))

    # Filtrado pasa-bajo de las señales
    b, a = butter(int(forden), (int(fc)/(fs/2)), btype = 'low')
    emg_fun_env_f = filtfilt(b, a, emg_fun_env)
    emg_cvm_env_f = filtfilt(b, a, emg_cvm_env)

    #calculando el valor máximo de emg_cvm y ajustando la señal EMG funcional
    emg_cvm_I = np.max(emg_cvm_env_f)
    emg_fun_norm = (emg_fun_env_f / emg_cvm_I) * 100
    
    return emg_fun_norm, emg_fun_env_f, emg_cvm_env_f


#%%

def plot_emgs(emg_fun, emg_fun_env, emg_fun_norm, emg_cvm, emg_cvm_env,
              fs, f_c, f_orden,
              nombre):
    """Grafica señales de EMG funcional y CVM.

    Parameters
    ----------
    emg_fun : array_like
        EMG funcional.
    emg_fun_env : array_like
        Envolvente del EMG funcional.
    emg_fun_norm : array_like
        EMG funcional normalizada según CVM.
    emg_cvm : array_like
        EMG contracción voluntaria máxima.
    fs : float
        Frecuencia de muestreo, en hertz.
    f_c : float
        Frecuencia de corte del filtro pasa-bajo, en hertz.
    f_orden : int
        Orden del filtro.
    nombre : str
        Nombre del gesto. 

    Notes
    -----
    Cambiados algunos tamaños y parte del título. Las líneas originales están 
    comentadas

    """
    # Tamaños de fuente
    titulo_size = 15
    label_size = 12
    
    # Vectores de tiempo
    t1 = np.arange(0, len(emg_fun) / fs, 1 / fs)
    t2 = np.arange(0, len(emg_cvm) / fs, 1 / fs)

    #fig, (ax1, ax2, ax3) = plt.subplots(3, 1,figsize = (8, 7))
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1,figsize=(4, 5))
    fig.canvas.manager.set_window_title('Normalización con CVM') 

    ax1.plot(t1, emg_fun, 'b', label='Señal bruta')
    #ax1.set_title(f'Músculo: {nombre};\nfiltro aplicado: f_c={f_c} [Hz] de 
    # 'f'orden {f_orden}')
    ax1.set_title(f'Gesto: {nombre};\nFiltro aplicado: f_c={f_c} [Hz] de\norden 
                  {f_orden}', fontsize = titulo_size)

    ax1.plot(t1, emg_fun_env, 'r', lw=2, label='Señal filtrada')
    ax1.set_ylabel(f'{nombre} Funcional\nAmplitud [V]',fontsize=label_size)
    #ax1.set_ylim(emg_fun.min() - 0.1, emg_fun.max() + 0.1)
    ax1.set_ylim(0, emg_fun.max() + 0.1)
    ax1.set_xlim(0, t1.max())
    ax1.grid()
    ax1.legend(loc='upper center', fontsize='x-small', borderpad=None)

    ax2.plot(t2, emg_cvm, 'b', label='Señal bruta')
    ax2.plot(t2, emg_cvm_env, 'r', lw=2, label='Señal filtrada')
    ax2.set_ylabel(f'{nombre} CVM\nAmplitud [V]',fontsize=label_size)
    ax2.axvline((np.argmax(emg_cvm_env) / fs), color='maroon')
    ax2.text(0.85, 0.95 ,f'Max = {emg_cvm_env.max():.2f}',
             transform=ax2.transAxes, ha="left", va="top")
    #ax2.set_ylim(emg_cvm.min() - 0.1, emg_cvm.max() + 0.1)
    #ax2.set_ylim(0, emg_cvm.max() + 0.1)
    ax2.set_xlim(0, t2.max())
    ax2.grid()
    ax2.legend(loc='upper center', fontsize='x-small', borderpad=None)

    ax3.plot(t1, emg_fun_norm, 'g',label='Señal ajustada según CVM')
    ax3.set_ylim(emg_fun_norm.min(), emg_fun_norm.max() + 2)
    ax3.set_xlim(0, t1.max())
    ax3.set_xlabel('Tiempo [s]', fontsize=label_size)
    ax3.set_ylabel('% EMG CVM')
    ax3.grid()
    ax3.legend(loc='upper center', fontsize='x-small', borderpad=None)

    plt.tight_layout(h_pad=.1)


#%% Nuevo: Función para calcular RMS
def get_rms(values):
    """
    Calcula el valor RMS de una lista de valores.

    Parameters
    ----------
        values (list or np.array): Lista de valores numéricos.

    Returns:
        float: El valor RMS de la lista.
    """
    values = np.array(values)
    rms = np.sqrt(np.mean(np.square(values)))
    return rms

#%% Nuevo: Función para calcular la SNR
import numpy as np

def get_SNR(signal_rms, noise_rms):
    """
    Calcula la relación señal a ruido (SNR) a partir de los valores RMS de la 
    señal y del ruido.

    Parameters
    ----------
        signal_rms (float): El valor RMS de la señal.
        noise_rms (float): El valor RMS del ruido.

    Returns:
        float: El valor de la SNR en decibeles (dB).
    """
    snr = 20 * np.log10(signal_rms / noise_rms)
    return snr



#%% 

def normalizar_3ch_sql(gesto_id, ruta_db = 'Datos/datos_gestos_3ch.db', 
                       tabla_raw = 'raw', fs = 1000, fc = 150, forden = 2, 
                       reescalado = 5.0/1023, canales = [1, 2, 3]):
    """
    Script para normalizar señales de hasta tres canales de un gesto específico 
    a partir de su ID, almacenado en una base de datos en SQLite.
    Requiere que en la base de datos existan hasta 3 canales de registros del 
    gesto a usar, un registro llamado 'Reposo' y otros llamados 'CVM CH1', 
    'CVM CH2' y 'CVM CH3, todos correspondiendo a la misma sesión en la que se 
    tomaron los registros

    Parameters
    ----------
        "gesto_id": Número identificador del gesto a normalizar
        "ruta_db": La ruta a la base de datos SQLite que por defecto es 
                   'Datos/datos_gestos_3ch.db'.
        "tabla_raw": El nombre de la tabla dentro de la base de datos donde se 
                     registran los datos brutos
        "fs": La frecuencia de muestreo, cuyo valor por defecto es 1000 Hz.
        "fc": La frecuencia de corte para el filtrado, cuyo valor por defecto es 
              150 Hz.
        "forden": El orden del filtro pasabajos, cuyo valor por defecto es 2.
        "reescalado": Factor para reescalar los datos, cuyo valor por defecto es 
                      de 5.0/1023 para una tarjeta que recibe hasta 5 volts en 
                      un ADC de 10 bits
        "canales": Lista de canales a analizar, que por defecto es [1, 2, 3]


    Este script realiza las siguientes operaciones:
    1. Conectar a la base de datos SQLite especificada.
    2. Obtener los datos de la señal para el "gesto_id" proporcionado.
    3. Filtrar las señales con la frecuencia y el orden especificado
    4. Calcular las envolventes de los 3 canales
    5. Normalizar las señales a partir de su contracción voluntaria máxima (CVM)


    Return
    ------
        datos_normalizados: array_like
            Un diccionario con las siguientes entradas:
                id (int)                  : Identificador único autoincremental 
                                            para cada entrada
                gesto_id (int)            : Identificador único para cada gesto. 
                                            Útil para diferenciar distintas 
                                            instancias del mismo gesto
                sesion_id (int)           : ID de la sesión en la que se hizo la 
                                            captura
                onset (list,int)          : Indicador de si se está ejecutando 
                                            el gesto. 1 para indicar que está en 
                                            ejecución
                nombre_gesto (string)     : Nombre del gesto hecho
                fs (int)                  : Frecuencia de muestreo en Hertz
                fc (int)                  : Frecuencia de corte del filtro 
                fecha (string)            : Fecha en la que se hizo la captura, 
                                            -MM-DD HH:MM:SS
                ch1_env_fil (list, float) :  Valores de la envolvente post 
                                             filtrado del canal 1
                ch1_norm (list,float)     :  Valores del canal 1 normalizado 
                                             respecto a la CVM correspondiente
                ch2_env_fil (list,float)  :  Valores de la envolvente post 
                                             filtrado del canal 2
                ch2_norm (list,float)     :  Valores del canal 2 normalizado 
                                             respecto a la CVM correspondiente
                ch3_env_fil (list,float)  :  Valores de la envolvente post 
                                             filtrado del canal 3
                ch3_norm (list,float)     :  Valores del canal 3 normalizado 
                                             respecto a la CVM correspondiente


"""
    # Conectarse a la base de datos
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()

    # Obtener datos del gesto funcional
    cursor.execute(f"""
            SELECT fs, fecha, onset, sesion_id, CH1, CH2, CH3, nombre_gesto 
            FROM {tabla_raw} 
            WHERE gesto_id = ?
            """, (gesto_id,))
    
    datos_gesto_funcional = cursor.fetchall()

    # Nuevo: ahora lee los 3 canales sin tener que ingresarlos manualmente
    canales = [1, 2, 3] 

    # Diccionario para ir registrando los datos que corresponden a cada canal
    df_funcional = {
        1: [],
        2: [],
        3: []
    }
    for num_canal in canales:
        # df_funcional[i] corresponde al canal i
        df_funcional[num_canal] = [dato[3 + num_canal] * reescalado 
                                   for dato in datos_gesto_funcional] 
        # Formato: [fs, fecha, onset, sesion_id, CH1, CH2, CH3, nombre_gesto ]
    
    # Clonar vector de onset del gesto. Este vector aplica para los 3 canales
    onset_funcional = [dato[2] for dato in datos_gesto_funcional] 
    
    # Estos datos son los mismos para los 3 canales a través de todo el tiempo
    fecha_captura = datos_gesto_funcional[0][1]
    sesion_id_gesto = datos_gesto_funcional[0][3]   
    nombre_gesto_funcional = datos_gesto_funcional[0][-1] 

    # Filtrar datos de CVM según el canal en uso y el número de sesión
    # Nuevo: ahora lee los 3 canales en lugar de solo uno
    datos_cvm = {1: [],2: [],3: []}
    df_cvm = {1: [],2: [],3: []}
    emg_funcional = {1: [],2: [],3: []}
    emg_cvm = {1: [],2: [],3: []}
    emg_f_n = {1: [],2: [],3: []}
    emg_f_env = {1: [],2: [],3: []}
    emg_cvm_env = {1: [],2: [],3: []}
    for num_canal in canales: 
        canal_string = "CH" + str(num_canal)
        # Este query retorna una lista con la ID del CVM, la fecha, su nombre, 
        # la sesión en la que se grabó y los valores del canal correspondiente
        cursor.execute(f"""
            SELECT gesto_id, fs, fecha, onset, sesion_id, {canal_string}, 
            nombre_gesto
            FROM {tabla_raw} 
            WHERE nombre_gesto LIKE '%CVM {canal_string}%'
            AND sesion_id = ?
        """,(sesion_id_gesto,))
        datos_cvm[num_canal] = cursor.fetchall()
        df_cvm[num_canal] = [dato[-2] * reescalado 
                             for dato in datos_cvm[num_canal]] 
        
        emg_funcional[num_canal] = np.array(df_funcional[num_canal])
        emg_cvm[num_canal] = np.array(df_cvm[num_canal])
        


        # Línea para invocar la función de ajuste
        emg_f_n[num_canal], 
        emg_f_env[num_canal], 
        emg_cvm_env[num_canal] = ajusta_emg_func(emg_funcional[num_canal],
                                                 emg_cvm[num_canal], fs, fc, 
                                                 forden)

        # emg_f_n: Señal emg normalizada respecto a la CVM
        # emg_f_env: Envolvente de la señal luego de ser filtrada 
        # emg_cvm_env: Envolvente de la señal CVM normalizada y filtrada

        # Valores a retornar:
        resultado_normalizado = {
        'gesto_id': gesto_id,
        'sesion_id': sesion_id_gesto,
        'fecha': fecha_captura,
        'nombre_gesto': nombre_gesto_funcional,
        'fs': fs,
        'fc': fc,
        'onset': onset_funcional,
        # Canal 1
        'ch1_env_fil'   : emg_f_env[1],# Envolvente después de filtrar señal EMG
        'ch1_norm'      : emg_f_n[1],  # Señal EMG normalizada respecto a la CVM
        # Canal 2
        'ch2_env_fil'   : emg_f_env[2],# Envolvente después de filtrar señal EMG
        'ch2_norm'      : emg_f_n[2],  # Señal EMG normalizada respecto a la CVM
        # Canal 3
        'ch3_env_fil'   : emg_f_env[3],# Envolvente después de filtrar señal EMG
        'ch3_norm'      : emg_f_n[3],  # Señal EMG normalizada respecto a la CVM
    }

    return resultado_normalizado

#%%

def registrar_datos_norm(datos_normalizados, 
                         ruta_db='Datos/datos_gestos_3ch.db', 
                         tabla_norm = 'norm'):
    """
    Registra los datos normalizados en la base de datos.

    Estructura de la base de datos
    ------------------------------
          id: Identificador único autoincremental para cada entrada
    gesto_id: Identificador único para cada gesto. Útil para diferenciar 
              distintas instancias del mismo gesto
   sesion_id: ID de la sesión en la que se hizo la captura
       fecha: Fecha en la que se hizo la captura, YYYY-MM-DD HH:MM:SS
nombre_gesto: Nombre del gesto hecho
          fs: Frecuencia de muestreo en Hertz (default: 1000)
          fc: Frecuencia de corte del filtro de 2do grado (default: 150)
       onset: Indicador de si se está ejecutando el gesto. 1 para indicar que 
              está en ejecución
    chX_norm: Valor del canal X normalizado respecto a la CVM correspondiente
 chX_env_fil: Valor de la envolvente post filtrado del canal X

    """
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()

    # Crear la tabla "norm" y ejecutar la consulta para crearla

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {tabla_norm} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gesto_id INTEGER,
        sesion_id INTEGER,
        fecha TEXT,
        nombre_gesto TEXT,
        fs INTEGER,
        fc INTEGER,
        onset INTEGER,
        ch1_norm REAL,
        ch1_env_fil REAL,
        ch2_norm REAL,
        ch2_env_fil REAL,
        ch3_norm REAL,
        ch3_env_fil REAL
    );
    """)

    # Descomponer y registrar los valores de cada canal
    n_registros = len(datos_normalizados['onset'])

    for i in range(n_registros):
        insertar_query = f"""
       INSERT INTO {tabla_norm} (gesto_id, sesion_id, fecha, nombre_gesto, fs, 
                                 fc, onset, ch1_env_fil, ch1_norm,
                                 ch2_env_fil, ch2_norm, ch3_env_fil, ch3_norm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        valores = (
            datos_normalizados['gesto_id'],
            datos_normalizados['sesion_id'],
            datos_normalizados['fecha'],
            datos_normalizados['nombre_gesto'],
            datos_normalizados['fs'],
            datos_normalizados['fc'],
            datos_normalizados['onset'][i],
            datos_normalizados['ch1_env_fil'][i],
            datos_normalizados['ch1_norm'][i],
            datos_normalizados['ch2_env_fil'][i],
            datos_normalizados['ch2_norm'][i],
            datos_normalizados['ch3_env_fil'][i],
            datos_normalizados['ch3_norm'][i],

        )
        cursor.execute(insertar_query, valores)

    
    conexion.commit()
    conexion.close()

    print(f"Registrado '{datos_normalizados['nombre_gesto']}' con ID 
          {datos_normalizados['gesto_id']} en la tabla '{tabla_norm}'.")



#%% 
'''
    Ejemplo de uso: Normalizar todos los registros en la base de datos 
'''
#if __name__ == '__main__':
def norm_db_sql():
    # Parámetros de frecuencia y orden de filtro
    tabla_raw = "raw"
    fs = 1e3    # Frecuencia de muestreo
    fc, forden = 150, 2 # Frecuencia de corte y orden del filtro pasabajos

    # Desplegar los gestos disponibles
    ruta_db = 'Datos/datos_gestos_3ch.db'
    # Factor de reescalado en caso de capturar con un ADC de otra resolución
    # 5.0/1023 es para un ADC de 10 bits que recibe hasta 5 volts
    reescalado = (5.0/1023) 
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()

    # Mostrar la ubicación de la base de datos
    print(f"Usando base de datos en: {os.path.abspath(ruta_db)}")

    # Inicio de interacción con usuario
    # Mostrar los gestos almacenados 
    cursor.execute(f"""
        SELECT gesto_id, MIN(fecha), nombre_gesto, sesion_id 
        FROM {tabla_raw} 
        GROUP BY gesto_id
    """)
    datos = cursor.fetchall()
    
    # Imprimir los datos obtenidos por consola
    print(f"""--- Gestos registrados ---
ID  \tFecha              \tSesión\tNombre del gesto
----\t-------------------\t------\t----------------""")
    gestos_a_registrar = []
    for fila in datos:
        gesto_id, fecha, gesto, sesion_id = fila
        print(f"{gesto_id}\t{fecha}\t{sesion_id}\t{gesto}")
        gestos_a_registrar.append(gesto_id)
    
    n_gestos = len(gestos_a_registrar)
    rpta = []
    while rpta not in ["y", "n"]:
        rpta = input(f"¿Normalizar los {n_gestos} gestos? [Y/n]: ").lower()

    # Fin de interacción con el usuario
    if rpta == "n":
        print("Cancelando...")
        quit()
    else:
        for gesto in gestos_a_registrar:
            # Normalizar todos los gestos 
            datos_norm = normalizar_3ch_sql(gesto, ruta_db, tabla_raw, fs, fc, 
                                            forden, reescalado, [1,2,3])
            registrar_datos_norm(datos_norm, ruta_db, 'norm')
    
    print(f"Finalizado. {n_gestos} gestos registrados.")



   # Cerrar la conexión a la base de datos
    conexion.close()

#%%
if __name__ == '__main__':
    '''
    Ejemplo para graficar usando las funciones propuestas y la base de datos.
    Se entrega una cierta interacción con el usuario al ofrecer la lista de 
    gestos y consultar por datos como ID de interés y canal a graficar.
    También sirve como un ejemplo de cómo hacerle una query a la base de datos y
    cómo reescalar los datos brutos
    '''
    ### Consultar gestos
    # Conectar a la base de datos SQLite
    db_path = 'Datos/datos_gestos_3ch.db'
    conexion = sqlite3.connect(db_path)
    tabla_raw = 'raw'
    tabla_norm = 'norm'
    cursor = conexion.cursor()
    reescalado = 5.0/1023
    fs = 1000   # Frecuencia de sampling en Hz
    f_c = 150   # Frecuencia de corte del filtro pasabajos en Hz
    f_orden = 2 # Orden del filtro pasabajos en Hz

    # Mostrar la ubicación de la base de datos en consola
    print(f"Usando base de datos en: {os.path.abspath(db_path)}")

    # Consultar los datos de gesto_id, fecha y gesto, omitiendo los gesto_id 
    # repetidos
    cursor.execute(f"""
        SELECT gesto_id, MIN(fecha), nombre_gesto, sesion_id 
        FROM {tabla_raw} 
        GROUP BY gesto_id
    """)
    datos = cursor.fetchall()

    # Imprimir los datos obtenidos por consola
    print(f"""--- Gestos registrados ---
ID  \tFecha              \tSesión\tNombre del gesto
----\t-------------------\t------\t----------------
    """)
    for fila in datos:
        gesto_id, fecha, gesto, sesion_id = fila
        print(f"{gesto_id}\t{fecha}\t{sesion_id}\t{gesto}")

    gesto_id = int(input("Por favor, introduce la ID del gesto a graficar: "))

    # Escoger el canal a graficar
    nro_canal = []
    canales = [1, 2, 3] 
    int(input("Por favor, introduce el canal a analizar [1, 2 o 3]: "))
    
        
    ### Obtener datos del gesto funcional bruto
    cursor.execute(f"""
            SELECT CH1 * {reescalado}, CH2 * {reescalado}, CH3 * {reescalado}, 
            nombre_gesto, sesion_id
            FROM {tabla_raw} 
            WHERE gesto_id = ?
            """, (gesto_id,))
    # datos_db es una variable auxiliar donde dejo lo que se retorna del query
    datos_db = cursor.fetchall() 
    
    # Nombre para el despliegue
    nombre = datos_db[0][-2]   

    # ID de sesión para obtener la CVM correspondiente
    sesion_id = datos_db[0][-1] 

    # Registrar los datos brutos a usar
    emg_fun_list = [dato[nro_canal - 1] for dato in datos_db] 
    emg_fun = np.array(emg_fun_list)

    

    ### Obtener la envolvente de la señal
    cursor.execute(f"""
        SELECT ch1_env_fil, ch2_env_fil, ch3_env_fil, sesion_id, nombre_gesto 
        FROM {tabla_norm} 
        WHERE gesto_id = ?
        """, (gesto_id,))
    datos_db = cursor.fetchall()

    # Registrar los datos de la envolvente del gesto a usar
    emg_fun_env_list = [dato[nro_canal - 1] for dato in datos_db] 
    emg_fun_env = np.array(emg_fun_env_list)


    ### Obtener la señal normalizada
    cursor.execute(f"""
        SELECT ch1_norm, ch2_norm, ch3_norm
        FROM {tabla_norm} 
        WHERE gesto_id = ?
        """, (gesto_id,))
    datos_db = cursor.fetchall()

    # Registrar los datos de la señal normalizada a usar
    emg_fun_norm_list = [dato[nro_canal - 1]for dato in datos_db] 
    emg_fun_norm = np.array(emg_fun_norm_list)


    ### Obtener la CVM bruta correspondiente
    # Para que quede en formato "CHX" como las columnas de la base de datos
    canal_string = str("CH" + str(nro_canal))    
    
    cursor.execute(f"""
        SELECT {canal_string} * {reescalado}
        FROM {tabla_raw} 
        WHERE nombre_gesto LIKE '%CVM {canal_string}%'
        AND sesion_id = ?
    """,(sesion_id,))

    # Registrar los datos de la CVM bruta
    emg_cvm_list = cursor.fetchall()
    emg_cvm = np.array(emg_cvm_list)
    #datos_db = cursor.fetchall()
    #emg_cvm = [dato[0] for dato in datos_db[nro_canal]] 


    ### Obtener la envolvente de la CVM
    cursor.execute(f"""
        SELECT ch1_env_fil, ch2_env_fil, ch3_env_fil
        FROM {tabla_norm} 
        WHERE nombre_gesto LIKE '%CVM {canal_string}%'
        AND sesion_id = ?
        """, (sesion_id,))
    
    datos_db = cursor.fetchall()

    # Registrar los datos de la envolvente del CVM correcto
    emg_cvm_env_list = [dato[nro_canal - 1] for dato in datos_db] 
    emg_cvm_env = np.array(emg_cvm_env_list)


    # Graficar
    mpl.rc('font',family='Times New Roman')
    plot_emgs(emg_fun, emg_fun_env, emg_fun_norm, emg_cvm, emg_cvm_env,
              fs, f_c, f_orden,
              nombre)
    
    # Guardar gráfico generado
    directorio = 'fig_3ch/cvm'
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    nombre_archivo = f"cvm_{gesto_id}_{nombre}_{canal_string}.png"
    ruta_archivo = os.path.join(directorio, nombre_archivo)
    plt.savefig(ruta_archivo)
    print(f"Guardando gráfico en {ruta_archivo}")

    # Mostrar la gráfica
    plt.show()
import sqlite3
import matplotlib.pyplot as plt

# Conectar a la base de datos SQLite
db_path = 'datos_3ch_gestos.db'
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Consultar y mostrar los nombres de los gestos disponibles en la base de datos
cursor.execute("SELECT DISTINCT nombre_gesto FROM datos")
gestos_disponibles = cursor.fetchall()

print("Gestos disponibles:")
for gesto in gestos_disponibles:
    print(f"- {gesto[0]}")

# Solicitar el nombre del gesto al usuario
nombre_gesto = input("Por favor, ingrese el nombre del gesto: ")

# Consultar los datos de timestamp, CH1, CH2 y CH3 que coincidan con el nombre del gesto especificado
cursor.execute("SELECT timestamp, CH1, CH2, CH3 FROM datos WHERE nombre_gesto = ?", (nombre_gesto,))
datos = cursor.fetchall()

# Separar los datos en listas individuales
timestamps = [fila[0] for fila in datos]
CH1 = [fila[1] for fila in datos]
CH2 = [fila[2] for fila in datos]
CH3 = [fila[3] for fila in datos]

# Crear una figura y paneles (subplots)
fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# Título general
fig.suptitle(f'Lecturas del gesto: {nombre_gesto}', fontsize=20)

# Graficar CH1
axs[0].plot(timestamps, CH1, label='CH1', color='blue')
axs[0].set_ylabel('Lectura CH1', fontsize=18)
axs[0].tick_params(axis='y', labelsize=14)
axs[0].grid(True)

# Graficar CH2
axs[1].plot(timestamps, CH2, label='CH2', color='green')
axs[1].set_ylabel('Lectura CH2', fontsize=18)
axs[1].tick_params(axis='y', labelsize=14)
axs[1].grid(True)

# Graficar CH3
axs[2].plot(timestamps, CH3, label='CH3', color='red')
axs[2].set_ylabel('Lectura CH3', fontsize=18)
axs[2].set_xlabel('Tiempo (ms)', fontsize=18)
axs[2].tick_params(axis='y', labelsize=14)
axs[2].tick_params(axis='x', labelsize=14)
axs[2].grid(True)

# Ajustar el layout
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Guardar gráfico
plt.savefig(f'graficos rawEMG/{nombre_gesto}.png')
print(f"Guardado gráfico en 'graficos rawEMG/{nombre_gesto}.png'")

# Mostrar el gráfico
plt.show()

# Cerrar la conexión a la base de datos
conexion.close()

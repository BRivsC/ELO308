''' Detección de 3 gestos

Script en Python para detectar qué gestos se están ejecutando. Pensado para 
funcionar con 3 canales, donde cada canal corresponde a 1 un grupo muscular 
y gesto.
Espera recibirlos con el formato <onset>,<CH1>,<CH2>,<CH3>,...

Uso
---
    - Posicionar equipo en el brazo y conectar a la computadora.
    - Verificar por monitor serial que la señal no sea ruidosa.
    - Ejecutar el script y observar la salida en la consola.
Bastián Rivas
'''
import serial

# Función para obtener el promedio luego de centrar los datos en cero y obtener su valor absoluto
def centrar_y_promediar(datos):
    datos_centrados = [dato - sum(datos) / len(datos) for dato in datos]
    return sum(abs(dato) for dato in datos_centrados) / len(datos_centrados)

# Configurar el puerto serial
puerto_serial = 'COM4' # Cambiar según el puerto utilizado
baud_rate = 115200

# Definir el valor umbral de activación para cada canal
umbral_ch1 = 15  # Flex. radial: levantar muñeca
umbral_ch2 = 26  # Ext. com. dedos: abrir mano
umbral_ch3 = 25  # Flex. dedos: puño/muñeca abajo

# Listas con tamaño definido para actuar como buffers
BUFFER_SIZE = 100

buffer_ch1 = [0] * BUFFER_SIZE
buffer_ch2 = [0] * BUFFER_SIZE
buffer_ch3 = [0] * BUFFER_SIZE

i = 0 # Contador para el buffer

# Variable para almacenar el último gesto detectado
ultimo_gesto = None
gesto_actual = None

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

                    # Asegurarse de que hay al menos tres valores (CH1, CH2, CH3)
                    if len(valores) >= 3:
                        try:
                            # Convertir los valores a enteros
                            ch1 = int(valores[1])
                            ch2 = int(valores[2])
                            ch3 = int(valores[3])

                            # Registrar los valores en el buffer
                            buffer_ch1[i] = ch1
                            buffer_ch2[i] = ch2
                            buffer_ch3[i] = ch3

                            # Lógica para detectar gestos
                            # Se ejecuta cada vez que reciben la cantidad de datos configurada en BUFFER_SIZE
                            if i == BUFFER_SIZE-1:
                                promedio_ch1 = centrar_y_promediar(buffer_ch1)
                                promedio_ch2 = centrar_y_promediar(buffer_ch2)
                                promedio_ch3 = centrar_y_promediar(buffer_ch3)

                                # Descomentar esta línea para ver los promedios
                                #print(f"Promedios:\tCH1: {promedio_ch1},\tCH2: {promedio_ch2},\tCH3: {promedio_ch3}")
                                if promedio_ch1 > umbral_ch1:
                                    gesto_actual = "Arriba"
                                #elif promedio_ch2 > umbral_ch2:
                                    #gesto_actual = "Mano abierta"
                                elif promedio_ch3 > umbral_ch3:
                                    gesto_actual = "Abajo"
                                else:
                                    gesto_actual = "Reposo"
                                i = 0

                            # Solo imprimir el gesto si se ha cambiado
                            if gesto_actual != ultimo_gesto:
                                print(gesto_actual)
                                ultimo_gesto = gesto_actual
                            i += 1

                        except ValueError:
                            print(f"Error al convertir los datos a enteros: {data}")
                    else:
                        print(f"Datos incompletos recibidos: {data}")

                except UnicodeDecodeError:
                    # Ignorar errores en la decodificación
                    pass

except serial.SerialException as e:
    print(f"Error al acceder al puerto serial: {e}")
except KeyboardInterrupt:
    print("\nLectura interrumpida. Saliendo...")
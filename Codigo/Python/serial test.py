import serial

# Configurar el puerto serial
puerto_serial = 'COM4'
baud_rate = 115200

# Abrir el puerto serial
try:
    with serial.Serial(puerto_serial, baud_rate, timeout=0) as ser:
        print(f"Leyendo desde {puerto_serial} a {baud_rate} baud...\n")
        while True:
            # Leer línea desde el puerto serial
            if ser.in_waiting > 0:
                data = ser.readline().rstrip()
                print(data)
except serial.SerialException as e:
    print(f"Error al acceder al puerto serial: {e}")
except KeyboardInterrupt:
    print("\nLectura interrumpida. Saliendo...")

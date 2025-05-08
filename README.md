# ELO308
Repositorio con los scripts de la memoria "Desarrollo de un sistema de sensores para prótesis biónicas"



### Descripción de Carpetas

- **Codigo/Arduino/**: Contiene los sketches de Arduino para la adquisición de señales EMG.
  - `BioAmp EMGFilter/`: Código para filtrar señales EMG utilizando un BioAmp EXG Pill. Utilizado principalmente como ejemplo
  - `EnvolventeEMG/`: Código para calcular la envolvente de señales EMG directamente desde el microcontrolador.
  - `Retornar_3_CH_ADC_wOnset/`: Código para capturar señales de 3 canales con detección de onset.

- **Codigo/Demo/**: Incluye un video demostrativo y un script para detectar gestos en tiempo real.

- **Codigo/Python/**: Scripts en Python para procesamiento y análisis offline de señales EMG.
  - `consultar_gestos.py`: Consulta los gestos registrados en la base de datos.
  - `emg_cvm_norm_sql.py`: Normaliza señales EMG respecto a la contracción voluntaria máxima (CVM).
  - `fft_datos_3ch.py`: Calcula y grafica la FFT de señales EMG.
  - `generar_tabla_fft_gestos.py`: Genera una tabla con las FFT de los gestos.
  - `graficar_datos_3ch.py`: Grafica señales EMG capturadas.
  - `graficar_fft_desde_db.py`: Grafica la FFT de gestos almacenados en la base de datos.
  - `lectura_3ch_rawEMG.py`: Captura señales EMG desde un puerto serial y las almacena en una base de datos.
  - `welch_datos_3ch.py`: Calcula la densidad espectral de potencia usando el método de Welch.

- **Diagramas/**: Diagramas y esquemas relacionados con el hardware utilizado en el proyecto.

- **Escrito/**: Documento PDF con el escrito asociado al proyecto

- **Modelos 3D/**: Archivos `.stl` con modelos 3D de los sensores y carcasas para portarlas.

## Requisitos

### Hardware
- Sensores EMG (como Gravity Analog EMG Sensor).
- Microcontrolador compatible con Arduino.
- Protoboard para conexiones.
- Pulsador y resistencia 10K.

### Software
- Python 3.x con las siguientes bibliotecas:
  - `numpy`
  - `matplotlib`
  - `scipy`
  - `sqlite3`
- Arduino IDE para cargar los sketches en el microcontrolador.

## Uso para captura de datos

1. **Adquisición de Datos**:
   - Cargar el sketch `Retornar_3_CH_ADC_wOnset` en el microcontrolador
   - Conectar los sensores.
   - Escribir el nombre del gesto a ejecutar.
   - Mantener pulsado el botón mientras se ejecuta el gesto.

2. **Procesamiento**:
   - Utilizar el script `emg_cvm_norm_sql.py` para normalizar los datos

3. **Visualización**:
   - Generar gráficos de las señales y sus transformadas (FFT, envolventes, etc.) con los scripts correspondientes.


## Autor

**Bastián Rivas**  
Ing. Civil Electrónica  
Universidad Técnica Federico Santa María, 2025

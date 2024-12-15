// Código para capturar señales EMG. Tomado del proyecto de BioAmp EXG Pill y
// modificado para funcionar con varios canales del Gravity Analog EMG Sensor de
// OyMotion.
// La salida sigue el formato <CH1_filtrado>,<CH1_envolvente>,<CH2_filtrado>,...
// Retorna las mediciones hechas en mV
// Bastián Rivas
// Ojo: incluye algunos comentarios en inglés de los autores originales
// Todo el crédito va a los respectivos autores.

// Disclaimer de la fuente:
// EMG Envelop - BioAmp EXG Pill
// https://github.com/upsidedownlabs/BioAmp-EXG-Pill

// Upside Down Labs invests time and resources providing this open source code,
// please support Upside Down Labs and open-source hardware by purchasing
// products from Upside Down Labs!

// Copyright (c) 2021 Upside Down Labs - contact@upsidedownlabs.tech

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

#define SAMPLE_RATE 500   // 1000 Hz funciona bien con 1CH, para más canales mejor usar 500 Hz
#define BAUD_RATE 115200
#define BUFFER_SIZE 128

//// Define el número de sensores
#define _N_SENSORES 1  // Cambiar este valor según el número de sensores en uso (entre 1 y 8)

// Pines de entrada para los sensores
int INPUT_PINS[_N_SENSORES];

//// Macro para analizar el tiempo que usan los filtros. Basado en el de OyMotion
//// Útil para ver si el número de canales y frec. de muestreo son viables
#define _DEBUG  0
#if _DEBUG
// Intervalo de tiempo para el procesado de la señal de entrada
unsigned long long intervaloProcesado = 1000000ul / SAMPLE_RATE;

// Tiempo restante 
long tiempoRestante;
#endif


void setup() {
  // Asignación dinámica de los pines de entrada según el número de sensores
  for (int i = 0; i < _N_SENSORES; i++) {
    INPUT_PINS[i] = A0 + i;
  }

  // Serial connection begin
  Serial.begin(BAUD_RATE);
}

// Variables para los buffers circulares y sus índices
int circular_buffer[_N_SENSORES][BUFFER_SIZE];
int data_index[_N_SENSORES], sum[_N_SENSORES];

void loop() {
  // Calculate elapsed time
  static unsigned long past = 0;
  unsigned long present = micros();
  unsigned long interval = present - past;
  past = present;

  // Run timer
  static long timer = 0;
  timer -= interval;

  // Sample and get envelop
  if (timer < 0) {
    timer += 1000000 / SAMPLE_RATE;
    for (int i = 0; i < _N_SENSORES; i++) {
      int sensor_value = analogRead(INPUT_PINS[i]) * (5000 / 1023); // en mV
      int signal = EMGFilter(sensor_value);
      int envelop = getEnvelop(i, abs(signal));

    #if !_DEBUG //  Salida normal del código si no se usa macro
    // Retorna salida cruda del sensor, señal post-filtrado y su envolvente
    // Descomentar según sea necesario
      // Serial.print(sensor_value); //  El valor crudo del sensor, centrado en 1,5V
		  // Serial.print(",");  
      //Serial.print("-500"); // Facilita lectura por monitor serial de Arduino
      //Serial.print(",");
      //Serial.print("500"); //  Facilita lectura por monitor serial de Arduino
      //Serial.print(",");
      Serial.print(signal); //  La señal tras pasar por los filtros
      Serial.print(",");
      Serial.print(envelop);  //  La envolvente de la señal
      if (i < _N_SENSORES - 1) {
        Serial.print(",");
      }
    #endif
    }
    Serial.println(); // Nueva línea después de procesar todos los sensores
  }

  // Macro para ver timing
  #if _DEBUG
    unsigned long tiempoTranscurrido = micros() - present;
    Serial.print("Costo de tiempo: ");
    Serial.print(tiempoTranscurrido);
    
    // El tiempo restante para hacer todo el procesamiento viene dado
    // por (intervalo - transcurrido).
    // Si es negativo, reducir la tasa de muestreo!
    tiempoRestante  = intervaloProcesado - tiempoTranscurrido;
    Serial.print("\tTiempo restante: ");
    Serial.println(tiempoRestante);
  
  #endif
}

// Envelop detection algorithm
int getEnvelop(int sensor, int abs_emg){
  sum[sensor] -= circular_buffer[sensor][data_index[sensor]];
  sum[sensor] += abs_emg;
  circular_buffer[sensor][data_index[sensor]] = abs_emg;
  data_index[sensor] = (data_index[sensor] + 1) % BUFFER_SIZE;
  return (sum[sensor] / BUFFER_SIZE) * 2;
}

// Band-Pass Butterworth IIR digital filter, generated using filter_gen.py.
// Sampling rate: 500.0 Hz, frequency: [74.5, 149.5] Hz.
// Filter is order 4, implemented as second-order sections (biquads).
// Reference: 
// https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html
// https://courses.ideate.cmu.edu/16-223/f2020/Arduino/FilterDemos/filter_gen.py
float EMGFilter(float input)
{
  float output = input;
  {
    static float z1, z2; // filter section state
    float x = output - 0.05159732*z1 - 0.36347401*z2;
    output = 0.01856301*x + 0.03712602*z1 + 0.01856301*z2;
    z2 = z1;
    z1 = x;
  }
  {
    static float z1, z2; // filter section state
    float x = output - -0.53945795*z1 - 0.39764934*z2;
    output = 1.00000000*x + -2.00000000*z1 + 1.00000000*z2;
    z2 = z1;
    z1 = x;
  }
  {
    static float z1, z2; // filter section state
    float x = output - 0.47319594*z1 - 0.70744137*z2;
    output = 1.00000000*x + 2.00000000*z1 + 1.00000000*z2;
    z2 = z1;
    z1 = x;
  }
  {
    static float z1, z2; // filter section state
    float x = output - -1.00211112*z1 - 0.74520226*z2;
    output = 1.00000000*x + -2.00000000*z1 + 1.00000000*z2;
    z2 = z1;
    z1 = x;
  }
  return output;
}

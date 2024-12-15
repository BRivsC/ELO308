#define SAMPLE_RATE 500   // 1000 Hz funciona bien con 1CH, para más canales mejor usar 500 Hz
#define BAUD_RATE 115200
#define BUFFER_SIZE 128

//// Pines de entrada para los tres canales
#define INPUT_PIN1 A0
#define INPUT_PIN2 A1
#define INPUT_PIN3 A2

//// Macro para probar timing de filtros. Basado en el de OyMotion
#define _DEBUG  1 
#if _DEBUG
// Intervalo de tiempo para el procesado de la señal de entrada
unsigned long long intervaloProcesado = 1000000ul / SAMPLE_RATE;

// Tiempo restante 
unsigned long tiempoRestante;
#endif

int circular_buffer1[BUFFER_SIZE], circular_buffer2[BUFFER_SIZE], circular_buffer3[BUFFER_SIZE];
int data_index1, data_index2, data_index3, sum1, sum2, sum3;

void setup() {
  // Serial connection begin
  Serial.begin(BAUD_RATE);
}

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
    int sensor_value1 = analogRead(INPUT_PIN1)*(5000/1023); // en mV
    int sensor_value2 = analogRead(INPUT_PIN2)*(5000/1023); // en mV
    int sensor_value3 = analogRead(INPUT_PIN3)*(5000/1023); // en mV

    int signal1 = EMGFilter(sensor_value1);
    int signal2 = EMGFilter(sensor_value2);
    int signal3 = EMGFilter(sensor_value3);

    int envelop1 = getEnvelop1(abs(signal1));
    int envelop2 = getEnvelop2(abs(signal2));
    int envelop3 = getEnvelop3(abs(signal3));

  #if !_DEBUG //  Salida normal del código si no se usa macro
    Serial.print(signal1); //  La señal del canal 1 tras pasar por los filtros
    Serial.print(",");
    Serial.print(envelop1);  //  La envolvente del canal 1
    Serial.print(",");
    Serial.print(signal2); //  La señal del canal 2 tras pasar por los filtros
    Serial.print(",");
    Serial.print(envelop2);  //  La envolvente del canal 2
    Serial.print(",");
    Serial.print(signal3); //  La señal del canal 3 tras pasar por los filtros
    Serial.print(",");
    Serial.println(envelop3);  //  La envolvente del canal 3
  #endif
  }

  // Macro para ver timing
  #if _DEBUG
    unsigned long tiempoTranscurrido = micros() - present;
    Serial.print("Costo de tiempo: ");
    Serial.print(tiempoTranscurrido);
    
    // El tiempo restante para hacer todo el procesamiento viene dado
    // por (intervalo - transcurrido).
    // Si falta tiempo, reducir la tasa de muestreo!
    tiempoRestante  = intervaloProcesado - tiempoTranscurrido;
    Serial.print("\tTiempo restante: ");
    Serial.println(tiempoRestante);
  
  #endif
}

// Envelop detection algorithm para el canal 1
int getEnvelop1(int abs_emg1){
  sum1 -= circular_buffer1[data_index1];
  sum1 += abs_emg1;
  circular_buffer1[data_index1] = abs_emg1;
  data_index1 = (data_index1 + 1) % BUFFER_SIZE;
  return (sum1/BUFFER_SIZE) * 2;
}

// Envelop detection algorithm para el canal 2
int getEnvelop2(int abs_emg2){
  sum2 -= circular_buffer2[data_index2];
  sum2 += abs_emg2;
  circular_buffer2[data_index2] = abs_emg2;
  data_index2 = (data_index2 + 1) % BUFFER_SIZE;
  return (sum2/BUFFER_SIZE) * 2;
}

// Envelop detection algorithm para el canal 3
int getEnvelop3(int abs_emg3){
  sum3 -= circular_buffer3[data_index3];
  sum3 += abs_emg3;
  circular_buffer3[data_index3] = abs_emg3;
  data_index3 = (data_index3 + 1) % BUFFER_SIZE;
  return (sum3/BUFFER_SIZE) * 2;
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

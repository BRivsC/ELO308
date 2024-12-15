#define SAMPLE_RATE 500
#define BAUD_RATE 115200
#define BUFFER_SIZE 128

//// Macro para probar timing de filtros. Basado en el de OyMotion
#define _DEBUG  1 
#if _DEBUG
// Intervalo de tiempo para el procesado de la señal de entrada
unsigned long long intervaloProcesado = 1000000ul / SAMPLE_RATE;

// Tiempo restante 
long tiempoRestante;
#endif


// Definimos los pines de entrada para varios canales
const int INPUT_PINS[] = {A0, A1, A2};  // Agrega más pines si es necesario
const int NUM_CHANNELS = sizeof(INPUT_PINS) / sizeof(INPUT_PINS[0]);

int circular_buffer[NUM_CHANNELS][BUFFER_SIZE];
int data_index[NUM_CHANNELS] = {0};
int sum[NUM_CHANNELS] = {0};

void setup() {
	Serial.begin(BAUD_RATE);
}

void loop() {
	static unsigned long past = 0;
	unsigned long present = micros();
	unsigned long interval = present - past;
	past = present;

	static long timer = 0;
	timer -= interval;

	if(timer < 0) {
		timer += 1000000 / SAMPLE_RATE;

		// Iterar sobre cada canal
		for (int i = 0; i < NUM_CHANNELS; i++) {
			int sensor_value = analogRead(INPUT_PINS[i]) * (5000 / 1023); // en mV
			int signal = EMGFilter(sensor_value);
			int envelop = getEnvelop(i, abs(signal));

  #if !_DEBUG //  Salida normal del código si no se usa macro

			Serial.print("CH");
			Serial.print(i + 1);  // Indicar canal
			Serial.print(": ");
			Serial.print(signal);
			Serial.print(", Envolvente: ");
			Serial.println(envelop);
  #endif

  //// Macro para ver timing
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
	}
}

int getEnvelop(int channel, int abs_emg) {
	sum[channel] -= circular_buffer[channel][data_index[channel]];
	sum[channel] += abs_emg;
	circular_buffer[channel][data_index[channel]] = abs_emg;
	data_index[channel] = (data_index[channel] + 1) % BUFFER_SIZE;
	return (sum[channel] / BUFFER_SIZE) * 2;
}

float EMGFilter(float input) {
	// Mismo filtro que en tu código original
	float output = input;
	{
		static float z1[NUM_CHANNELS], z2[NUM_CHANNELS];
		float x = output - 0.05159732 * z1[0] - 0.36347401 * z2[0];
		output = 0.01856301 * x + 0.03712602 * z1[0] + 0.01856301 * z2[0];
		z2[0] = z1[0];
		z1[0] = x;
	}
	// (repite el filtro si es necesario, como en tu código original)
	return output;
}

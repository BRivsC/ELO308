const int analogPin = A0;       // Pin de la señal
float envelope = 0.0;           // Variable para almacenar la envolvente
float alpha = 0.06;             // Constante de suavizado (para el filtro pasa-bajos), ajusta según la frecuencia de tu señal

void setup() {
  Serial.begin(115200);
}

void loop() {
  // Lee la señal en el pin A0 (valores entre 0 y 1023)
  int signal = analogRead(analogPin);

  // Convierte la señal a una escala bipolar (-512 a +512), solo si la señal es AC y está centrada en 512
  int centeredSignal = signal - 322;

  // Paso 1: Rectificación (valor absoluto de la señal)
  int rectifiedSignal = abs(centeredSignal);

  // Paso 2: Filtro pasa-bajos para suavizar y obtener la envolvente
  envelope = alpha * rectifiedSignal + (1 - alpha) * envelope;

  // Señal cruda
  Serial.print("Raw:");
  Serial.println(signal);

  Serial.print("Centered:");
  Serial.println(centeredSignal);

  // Imprime el valor de la envolvente
  Serial.print("\tEnvelope:");
  Serial.println(envelope);

  // Ajusta el tiempo de muestreo según la frecuencia de tu señal
  delay(1);
}

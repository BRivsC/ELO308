/*  Retornar lectura de ADC de 3 canales + función de Onset
  Sketch de Arduino para retornar por consola serial los valores recibidos desde los ADCs.
  Retorna valores según lo recibido en cada pin analógico
  Incluye una función para mantener pulsado un botón y mandar su estado por serial
*/

#define SAMPLE_FREQ 1000 // Frecuencia de muestreo en Hz

// Definición de pines
#define CH1_PIN A0
#define CH2_PIN A1
#define CH3_PIN A2
#define ONSET_PIN A3

// Configuración inicial
void setup() {
  // Inicializar la comunicación serial a 115200 baud
  Serial.begin(115200);
  
  // Configurar los pines A0, A1, A2 y A3 como entradas
  pinMode(CH1_PIN, INPUT); // Canal 1
  pinMode(CH2_PIN, INPUT); // Canal 2
  pinMode(CH3_PIN, INPUT); // Canal 3
  pinMode(ONSET_PIN, INPUT); // Onset (1 si se mantiene pulsado el botón)
}


// Bucle principal
void loop() {
  // Leer los valores analógicos desde los pines A0, CH2_PIN y A2
  int sensorValue1 = analogRead(CH1_PIN); // Canal 1
  int sensorValue2 = analogRead(CH2_PIN); // Canal 2
  int sensorValue3 = analogRead(CH3_PIN); // Canal 3
  
  // Leer estado del botón de onset
  // Mantenerlo presionado mientras se haga un gesto
  int onset = digitalRead(ONSET_PIN);

  // Enviar los valores de voltaje a través de la consola serial
  // Formato: <onset>,<CH1>,<CH2>,<CH3>
  Serial.print(onset);
  //Serial.print(",");
  //Serial.print("1023");
  Serial.print(",");
  Serial.print(sensorValue1);
  Serial.print(",");
  Serial.print(sensorValue2);
  Serial.print(",");
  Serial.println(sensorValue3);
  
  // Frecuencia de muestreo
  delay(1000/SAMPLE_FREQ);
}

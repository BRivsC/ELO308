/*
  Sketch de Arduino para retornar por consola serial los valores recibidos desde los ADCs.
  Retorna valores según la frecuencia de muestreo (en Hz)
  Ojo: Al comparar placas puede que los valores no parezcan consistentes por la distinta cantidad
       de bits de sus ADCs!
*/

#define SAMPLE_FREQ 1000
// Configuración inicial
void setup() {
  // Inicializar la comunicación serial a 9600 baud
  Serial.begin(115200);
  
  // Configurar los pines A0, A1 y A2 como entradas
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  pinMode(A2, INPUT);
}

// Bucle principal
void loop() {
  // Leer los valores analógicos desde los pines A0, A1 y A2
  int sensorValue1 = analogRead(A0);
  int sensorValue2 = analogRead(A1);
  int sensorValue3 = analogRead(A2);
  
  // Convertir los valores analógicos a voltaje
  //float voltage1 = sensorValue1 * (5.0 / 1023.0);
  //float voltage2 = sensorValue2 * (5.0 / 1023.0);
  //float voltage3 = sensorValue3 * (5.0 / 1023.0);
  
  // Enviar los valores de voltaje a través de la consola serial
  //Serial.print("6");
  //Serial.print(",");
  //Serial.print("-1");
  //Serial.print(",");
  Serial.print(sensorValue1);
  Serial.print(",");
  Serial.print(sensorValue2);
  Serial.print(",");
  Serial.println(sensorValue3);
  
  // Frecuencia de muestreo
  delay(1000/SAMPLE_FREQ);
}

#include <Arduino.h>

const int PINO = 2; // D2 (também o LED onboard na maioria das placas ESP32)
unsigned long contador = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PINO, OUTPUT);
  digitalWrite(PINO, LOW);
  Serial.println("Gerador de pulsos iniciado no D2...");
}

void loop() {
  // Gera o pulso (50 ms em HIGH)
  digitalWrite(PINO, HIGH);
  delay(50);
  digitalWrite(PINO, LOW);

  contador++;
  Serial.print("Pulso: ");
  Serial.println(contador);

  // Intervalo entre pulsos (ex: 1 segundo)
  delay(1000);
}
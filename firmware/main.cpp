#include <Arduino.h>

const int PINO = 15;

void setup() {
  Serial.begin(115200);
  pinMode(PINO, INPUT_PULLUP);
}

void loop() {
  Serial.println(digitalRead(PINO));
  delay(200);
}

#include <Arduino.h>

const int PINO = 2;

// Conversão do hidrômetro
const float LITROS_POR_PULSO = 0.10;

// Intervalo para calcular a vazão
const unsigned long INTERVALO = 10000; // 10 segundos

unsigned long contador = 0;
unsigned long contadorAnterior = 0;

unsigned long tempoAnterior = 0;

float litros = 0;
float vazao = 0;

void setup() {

    Serial.begin(115200);

    pinMode(PINO, OUTPUT);
    digitalWrite(PINO, LOW);

    tempoAnterior = millis();

    Serial.println("Gerador de pulsos iniciado!");
}

void loop() {

    // =========================
    // GERA UM PULSO
    // =========================

    digitalWrite(PINO, HIGH);
    delay(50);

    digitalWrite(PINO, LOW);

    contador++;

    Serial.print("Pulso total: ");
    Serial.println(contador);

    // Espera aproximadamente 1 segundo
    delay(1000);


    // =========================
    // CALCULA A VAZAO
    // =========================

    if (millis() - tempoAnterior >= INTERVALO) {

        // Quantidade de pulsos ocorridos
        unsigned long pulsosIntervalo =
            contador - contadorAnterior;

        // Converte pulsos para litros
        litros = pulsosIntervalo * LITROS_POR_PULSO;

        // Calcula vazão em L/min
        vazao = (litros / 10.0) * 60.0;

        Serial.println("-------------------------");

        Serial.print("Pulsos no intervalo: ");
        Serial.println(pulsosIntervalo);

        Serial.print("Litros no intervalo: ");
        Serial.println(litros);

        Serial.print("Vazao: ");
        Serial.print(vazao);
        Serial.println(" L/min");

        Serial.println("-------------------------");


        // Atualiza os valores para o próximo intervalo
        contadorAnterior = contador;
        tempoAnterior = millis();
    }
}

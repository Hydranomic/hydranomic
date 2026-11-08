#include <WiFi.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

// Pinos dos LEDs de status
const int PIN_LED_VERDE = 4;     // Sucesso de conexao/envio
const int PIN_LED_AMARELO = 19;   // Erro de conexao WiFi
const int PIN_LED_VERMELHO = 21; // Erro de conexao com Broker WEGnology ou envio de dados

// Conexão esp com sensor
int SENSOR = 15;

int leituraHidrometro;
int estadoAnterior = HIGH;

int count = 0;
int id = 1;

// Conexão esp e broker
const char* WIFI_SSID = "Nicolle";
const char* WIFI_PASSWORD = "Nicolle13";

/////////////////////////////////////////////////////////////
const char* MQTT_SERVER = "broker.app.wnology.io";
const char* MQTT_ACCESS_KEY = "aa6fa6d5-f77d-46da-b4e4-f23bf995d04f";
const char* MQTT_ACCESS_SECRET = "77547f8f4f0d805edeb1982eadf46251d6bf0bf8b565b9e3c7fd92746459807b";
const char* DEVICE_ID = "6aa2e97be257647a5e068ae4";
const char* MQTT_TOPIC = "wnology/6aa2e97be257647a5e068ae4/state";
const int MQTT_PORT = 1883;
const int PUBLISH_INTERVAL = 300000;

WiFiClient espClient;
PubSubClient client(espClient);

char attributes[200];

void connectWiFi();
void connectMQTT();
void publishData();

void desconnectWifi();
void desconnectClient();

void setLedStatus(bool verde, bool amarelo, bool vermelho);
void sinalizarErroWifi();
void sinalizarErroBrokerOuEnvio();
void sinalizarSucesso();

void setup() {
  // Inicializa os pinos dos LEDs apagados
  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_LED_AMARELO, OUTPUT);
  pinMode(PIN_LED_VERMELHO, OUTPUT);
  setLedStatus(false, false, false);

  pinMode(SENSOR, INPUT_PULLUP);
  Serial.begin(115200);
  client.setKeepAlive(100);
  client.setServer(MQTT_SERVER, MQTT_PORT);
  estadoAnterior = digitalRead(SENSOR);

  connectWiFi();
  connectMQTT();
  // //envio imediato de mensagens pequenas como JSONs de IoT
  // espClient.setNoDelay(true);
  desconnectWifi();
  desconnectClient();
}

void loop() {

  leituraHidrometro = digitalRead(SENSOR);

  if (leituraHidrometro == LOW && estadoAnterior == HIGH) {

    count++;

    Serial.print("Pulso: ");
    Serial.println(count);

    connectWiFi();
    connectMQTT();
    publishData();
    desconnectWifi();
    desconnectClient();
  }

  //Processa o ping do Keepalive (precisa rodar em todo ciclo)
  client.loop();

  estadoAnterior = leituraHidrometro;

}

// Funcoes de controle dos LEDs
void setLedStatus(bool verde, bool amarelo, bool vermelho) {
  digitalWrite(PIN_LED_VERDE, verde ? HIGH : LOW);
  digitalWrite(PIN_LED_AMARELO, amarelo ? HIGH : LOW);
  digitalWrite(PIN_LED_VERMELHO, vermelho ? HIGH : LOW);
}

void sinalizarErroWifi() {
  Serial.println(">>> STATUS LED: AMARELO (Erro de WiFi)");
  setLedStatus(false, true, false); // Liga apenas LED Amarelo (pino 5)
}

void sinalizarErroBrokerOuEnvio() {
  Serial.println(">>> STATUS LED: VERMELHO (Erro de Broker/Envio)");
  setLedStatus(false, false, true); // Liga apenas LED Vermelho (pino 19)
}

void sinalizarSucesso() {
  Serial.println(">>> STATUS LED: VERDE (Sucesso)");
  setLedStatus(true, false, false); // Liga apenas LED Verde (pino 4)
}

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int tentativas = 0;

  // Aguarda tentar conectar ao WiFi (ate 15 tentativas de 500ms)
  while (WiFi.status() != WL_CONNECTED && tentativas < 15) {
    delay(500);
    Serial.println("Connecting to WiFi...");
    tentativas++;
  }

  if (WiFi.status() == WL_CONNECTED && WiFi.localIP() != IPAddress(0, 0, 0, 0)) {
    Serial.println("Connected to WiFi network");
    Serial.println("-------------");
    WiFi.setSleep(false);
    delay(500); // Aguarda estabilizar o DNS do roteador para evitar falso erro -2
  } else {
    Serial.println("Failed to connect to WiFi");
    sinalizarErroWifi(); // Acende LED Amarelo
  }
}

void connectMQTT() {
  // 1. Se o WiFi nao estiver conectado ou sem IP, o erro e de WiFi (LED Amarelo)
  if (WiFi.status() != WL_CONNECTED || WiFi.localIP() == IPAddress(0, 0, 0, 0)) {
    sinalizarErroWifi();
    return;
  }

  client.setServer(MQTT_SERVER, MQTT_PORT);
  int tentativas = 0;

  while (!client.connected() && tentativas < 3) {
    // Se o WiFi cair no meio das tentativas do Broker, prioriza o erro de WiFi (Amarelo)
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi lost during MQTT connection");
      sinalizarErroWifi();
      return;
    }

    Serial.println("Connecting to MQTT server...");
    if (client.connect(DEVICE_ID, MQTT_ACCESS_KEY, MQTT_ACCESS_SECRET)) {
      Serial.println("Connected to WEGNOLOGY platform");
      Serial.println("-------------");
    } else {
      Serial.print("Failed to connect to WEGNOLOGY platform, error code: ");
      Serial.println(client.state());
      tentativas++;
      delay(2000);
    }
  }

  // Define o LED apos finalizar as tentativas
  if (client.connected()) {
    sinalizarSucesso(); // Acende LED Verde
  } else if (WiFi.status() != WL_CONNECTED) {
    sinalizarErroWifi(); // Se falhou porque o WiFi caiu -> LED Amarelo
  } else {
    sinalizarErroBrokerOuEnvio(); // Se o WiFi continua OK mas o Broker recusou/falhou -> LED Vermelho
  }
}

void publishData() {
  if (WiFi.status() != WL_CONNECTED) {
    sinalizarErroWifi();
    return;
  }

  if (!client.connected()) {
    sinalizarErroBrokerOuEnvio();
    return;
  }

  DynamicJsonDocument doc(200);
  doc["data"]["ID"] = id;
  doc["data"]["Pulsos"] = count;

  String payload;
  serializeJson(doc, payload);
  payload.toCharArray(attributes, 200);
  Serial.println(payload);

  if (client.connected() && count % 10 == 0) {
    if (client.publish(MQTT_TOPIC, attributes)) {
      Serial.println("****PULSO ENVIADA******");
      sinalizarSucesso(); // Acende LED Verde no envio com sucesso
    } else {
      Serial.println("****ERRO AO ENVIAR PULSO******");
      sinalizarErroBrokerOuEnvio(); // Acende LED Vermelho se o envio falhar
    }
  }
}

void call_pub() {
  if (!client.connected()) {
    Serial.println("Reconnecting to WEGNOLOGY platform");
    connectMQTT();
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Reconnecting to WiFi");
    connectWiFi();
  }

  client.loop();
  publishData();
  Serial.println("-------------");
}

void desconnectWifi() {
  // Desconecta limpando o status para que quedas futuras de WiFi sejam detectadas corretamente
  WiFi.disconnect(true, true);
}

void desconnectClient() {
  client.disconnect();
}
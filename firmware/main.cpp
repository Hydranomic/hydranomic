#include <WiFi.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <Preferences.h>

// Pinos dos LEDs de status
const int PIN_LED_VERDE = 4;     // Sucesso continuo de envio
const int PIN_LED_AMARELO = 5;   // Erro de conexao WiFi (status == false)
const int PIN_LED_VERMELHO = 19; // Erro de conexao com Broker WEGnology ou envio de dados

int SENSOR = 13;
int leituraHidrometro;
int estadoAnterior = HIGH;

int count = 0;
int id = 1;

Preferences prefs;

const char* WIFI_SSID = "Nicolle";
const char* WIFI_PASSWORD = "Nicolle13";

const char* MQTT_SERVER = "broker.app.wnology.io";
const char* MQTT_ACCESS_KEY = "aa6fa6d5-f77d-46da-b4e4-f23bf995d04f";
const char* MQTT_ACCESS_SECRET = "77547f8f4f0d805edeb1982eadf46251d6bf0bf8b565b9e3c7fd92746459807b";
const char* DEVICE_ID = "6aa2e97be257647a5e068ae4";
const char* MQTT_TOPIC = "wnology/6aa2e97be257647a5e068ae4/state";
const int MQTT_PORT = 1883;
const int PUBLISH_INTERVAL = 300000; // 5 minutos em milissegundos
const int INTERVALO_LITROS = 100;

WiFiClient espClient;
PubSubClient client(espClient);

char attributes[200];
unsigned long ultimoEnvio = 0;

// Prototipos das funcoes
bool connectWiFi();
bool connectMQTT();
bool publishData();
void setLedStatus(bool verde, bool amarelo, bool vermelho);
void sinalizarErroWifi();
void sinalizarErroBrokerOuEnvio();
void sinalizarSucesso();
void desconnectWifi();
void desconnectClient();

void setup() {
  // Configuracao dos LEDs de status
  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_LED_AMARELO, OUTPUT);
  pinMode(PIN_LED_VERMELHO, OUTPUT);

  // Inicializa LEDs apagados durante o boot
  setLedStatus(false, false, false);

  pinMode(SENSOR, INPUT_PULLUP);
  Serial.begin(115200);
  delay(100);

  prefs.begin("hidro", false);
  count = prefs.getInt("pulsos", 0);
  client.setKeepAlive(100);
  client.setServer(MQTT_SERVER, MQTT_PORT);
  estadoAnterior = digitalRead(SENSOR);

  Serial.println("Iniciando conexoes...");

  // Conecta ao WiFi com tratamento de erro
  if (connectWiFi()) {
    // Conecta ao Broker WEGnology com tratamento de erro
    if (connectMQTT()) {
      // Envio inicial de sincronizacao para confirmar status de sucesso
      publishData();
    }
  }
}

void loop() {
  // 1. Verificacao de status da conexao WiFi
  if (WiFi.status() != WL_CONNECTED) {
    sinalizarErroWifi();
    Serial.println("WiFi desconectado! Tentando reconectar...");
    connectWiFi();
    return;
  }
 
  // 2. Verificacao de conexao com o Broker WEGnology (se WiFi estiver OK)
  if (!client.connected()) {
    sinalizarErroBrokerOuEnvio();
    Serial.println("Broker WEGnology desconectado! Tentando reconectar...");
    connectMQTT();
  } else {
    client.loop();
  }

  // 3. Leitura e contagem de pulsos do hidrometro
  leituraHidrometro = digitalRead(SENSOR);

  if (leituraHidrometro == LOW && estadoAnterior == HIGH) {
    count++;
    prefs.putInt("pulsos", count);
    Serial.print("Pulso: ");
    Serial.println(count);

    // Envia dados se atingir o intervalo de litros estipulado
    if (count % INTERVALO_LITROS == 0) {
      publishData();
      ultimoEnvio = millis();
    }
    delay(50); // Debounce basico para o sensor de pulso
  }

  // 4. Envio periodico para manter telemetria frequente mesmo sem fluxo de pulsos
  if (millis() - ultimoEnvio >= PUBLISH_INTERVAL) {
    ultimoEnvio = millis();
    Serial.println("Realizando envio periodico de dados...");
    publishData();
  }

  estadoAnterior = leituraHidrometro;
}

// Funcoes de controle visual dos LEDs
void setLedStatus(bool verde, bool amarelo, bool vermelho) {
  digitalWrite(PIN_LED_VERDE, verde ? HIGH : LOW);
  digitalWrite(PIN_LED_AMARELO, amarelo ? HIGH : LOW);
  digitalWrite(PIN_LED_VERMELHO, vermelho ? HIGH : LOW);
}

void sinalizarErroWifi() {
  // WiFi false/desconectado: liga apenas LED Amarelo (pin 5)
  setLedStatus(false, true, false);
}

void sinalizarErroBrokerOuEnvio() {
  // Erro no Broker ou no envio de dados (com WiFi OK): liga apenas LED Vermelho (pin 19)
  setLedStatus(false, false, true);
}

void sinalizarSucesso() {
  // Mensagens enviadas com sucesso: mantem LED Verde aceso (pin 4)
  setLedStatus(true, false, false);
}

// Conexao WiFi com timeout e retorno de status
bool connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    return true;
  }

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando ao WiFi");

  unsigned long startAttemptTime = millis();
  // Aguarda conexao por ate 10 segundos
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Conectado com sucesso a rede WiFi!");
    Serial.println("-------------");
    WiFi.setSleep(false);
    return true;
  } else {
    Serial.println("Falha ao conectar ao WiFi (status == false).");
    sinalizarErroWifi();
    return false;
  }
}

// Conexao MQTT com timeout por tentativas e retorno de status
bool connectMQTT() {
  if (client.connected()) {
    return true;
  }

  // Se o WiFi nao estiver conectado, o erro prioritario e o WiFi
  if (WiFi.status() != WL_CONNECTED) {
    sinalizarErroWifi();
    return false;
  }

  client.setServer(MQTT_SERVER, MQTT_PORT);
  int tentativas = 0;

  while (!client.connected() && tentativas < 3) {
    tentativas++;
    Serial.print("Tentativa de conexao ao Broker WEGnology (");
    Serial.print(tentativas);
    Serial.println("/3)...");

    if (client.connect(DEVICE_ID, MQTT_ACCESS_KEY, MQTT_ACCESS_SECRET)) {
      Serial.println("Conectado a plataforma WEGNOLOGY!");
      Serial.println("-------------");
      return true;
    } else {
      Serial.print("Falha na conexao com a WEGNOLOGY. Codigo de erro: ");
      Serial.println(client.state());
      delay(1500);
    }
  }

  // Falha na conexao com o broker apos tentativas
  Serial.println("Erro persistente ao conectar no broker WEGnology.");
  sinalizarErroBrokerOuEnvio();
  return false;
}

// Publicacao de dados com tratamento de erro e sinalizacao
bool publishData() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Nao foi possivel publicar: WiFi desconectado.");
    sinalizarErroWifi();
    return false;
  }

  if (!client.connected()) {
    Serial.println("Nao foi possivel publicar: Broker desconectado.");
    sinalizarErroBrokerOuEnvio();
    return false;
  }

  DynamicJsonDocument doc(200);
  doc["data"]["ID"] = id;
  doc["data"]["Pulsos"] = count;

  String payload;
  serializeJson(doc, payload);
  payload.toCharArray(attributes, 200);
  Serial.print("Enviando payload: ");
  Serial.println(payload);

  bool enviado = client.publish(MQTT_TOPIC, attributes);
  if (enviado) {
    Serial.println("**** MENSAGEM ENVIADA COM SUCESSO ******");
    sinalizarSucesso(); // Liga o LED Verde (pin 4)
    return true;
  } else {
    Serial.println("**** ERRO NO ENVIO DOS DADOS AO BROKER ******");
    sinalizarErroBrokerOuEnvio(); // Liga o LED Vermelho (pin 19)
    return false;
  }
}

void desconnectWifi() {
  WiFi.disconnect();
}

void desconnectClient() {
  client.disconnect();
}

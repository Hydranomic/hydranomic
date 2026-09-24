#include <WiFi.h>

#include <ArduinoJson.h>
#include <PubSubClient.h>

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

void setup() {
  pinMode(SENSOR, INPUT);
  Serial.begin(115200);
  client.setKeepAlive(100);
  client.setServer(MQTT_SERVER, MQTT_PORT);

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
    //Processa o ping do Keepalive (precisa rodar em todo ciclo)
    client.loop();
    delay(100);
}

estadoAnterior = leituraHidrometro;

}

void connectMQTT() {
  client.setServer(MQTT_SERVER, MQTT_PORT);
  while (!client.connected()) {
    Serial.println("Connecting to MQTT server...");
    if (client.connect(DEVICE_ID, MQTT_ACCESS_KEY, MQTT_ACCESS_SECRET)) {
      Serial.println("Connected to WEGNOLOGY platform");
      Serial.println("-------------"); 
    } else {
      Serial.print("Failed to connect to WEGNOLOGY platform, error code: ");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi network");
  Serial.println("-------------"); 

  // Força o rádio a ficar 100% ativo sem dormir
  //WiFi.setSleep(false);
}


void publishData() {


  DynamicJsonDocument doc(200);
  doc["data"]["ID"] = id;
  doc["data"]["Pulsos"] = count;

  String payload;
  serializeJson(doc, payload);
  payload.toCharArray(attributes, 200);
  Serial.println(payload);

  if (client.connected() && count % 10 == 0) {
      client.publish(MQTT_TOPIC, attributes);
      Serial.println("****PULSO ENVIADA******");
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


void desconnectWifi (){
    WiFi.disconnect();
}

void desconnectClient(){
  client.disconnect();
}

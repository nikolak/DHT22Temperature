#include <DHT.h>
#include <ESP8266WiFi.h>

#define DHTPIN 2 // D4

const char ssid[]     = "your wifi SSID";
const char password[] = "wifi password";

const char host[] = "host IP";
const char privateKey[] = "private key";


DHT dht(DHTPIN, DHT22);
WiFiClient client;

void setup() {
  Serial.begin(115200);
  delay(10);
  connectToWifi();
  dht.begin();
}

void connectToWifi() {
  Serial.print("Connecting to ");
  Serial.print(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}


void getValues(float *ret) {
  float humidity = dht.readHumidity();
  float celsius = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  float fahrenheit = dht.readTemperature(true);

  // Check if any reads failed and exit early (to try again).
  if (isnan(humidity) || isnan(celsius) || isnan(fahrenheit)) {
    Serial.println("Failed to read from DHT sensor!");
    ret[5] = false; // failure
    return;
  }

  // Compute heat index in Fahrenheit (the default)
  float hif = dht.computeHeatIndex(fahrenheit, humidity);
  // Compute heat index in Celsius (isFahreheit = false)
  float hic = dht.computeHeatIndex(celsius, humidity, false);

  ret[0] = humidity;
  ret[1] = celsius;
  ret[2] = fahrenheit;
  ret[3] = hif;
  ret[4] = hic;
  ret[5] = true; //success
}

void postData(float *data){

  if(client.connect(host, 5000)){
      String encData = "&key=";
      encData += privateKey;
      encData += "&humidity=";
      encData += data[0];
      encData += "&celsius=";
      encData += data[1];
      encData += "&fahrenheit=";
      encData += data[2];
      encData += "&hic=";
      encData += data[3];
      encData += "&hif=";
      encData += data[4];

      client.print("POST /api/v1/update/ HTTP/1.1\n");
      client.print("Host: http://nikolak.com\n");
      client.print("Connection: close\n");
      client.print("Content-Type: application/x-www-form-urlencoded\n");
      client.print("Content-Length: ");
      client.print(encData.length());
      client.print("\n\n");
      client.print(encData);
      Serial.println("Data sent.");
  }else{
    Serial.println("Couldn't connect to the host");
  }

}

void loop() {
  delay(10000);

  float data[6] = {};

  if(WiFi.status() != WL_CONNECTED){
    connectToWifi();
  }

  getValues(data);

  if (!data[5]) {
    return;
  }

  Serial.print("Humidity: ");
  Serial.print(data[0]);
  Serial.print(" %\t");
  Serial.print("Temperature: ");
  Serial.print(data[1]);
  Serial.print(" *C ");
  Serial.print(data[2]);
  Serial.print(" *F\t");
  Serial.print("Heat index: ");
  Serial.print(data[3]);
  Serial.print(" *C ");
  Serial.print(data[4]);
  Serial.println(" *F");
  //postData(data);

}



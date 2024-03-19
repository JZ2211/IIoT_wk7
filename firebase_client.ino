
/**
 *
 * Github: https://github.com/mobizt/Firebase-ESP-Client
 * Copyright (c) 2023 mobizt
 * 
 *
 * Modified March 2024
 * by Jin Zhu
 *
 */

#include <Arduino.h>
#if defined(ESP32)
#include <WiFi.h>
#elif defined(ESP8266)
#include <ESP8266WiFi.h>
#endif
#include <Firebase_ESP_Client.h>

//libraries for BME280
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

// Provide the token generation process info.
#include <addons/TokenHelper.h>

/************* Please modify for your own project below *****************************************/
/* Please modify the WiFi credentials */
#define WIFI_SSID "WiFi Network Name"  
#define WIFI_PASSWORD "password" 

/* Please modify the API Key and Realtime Database URL for Firebase */
#define API_KEY "API key for your project"
#define DATABASE_URL "your_realtime_database.firebaseio.com" 

/* Please setup the user Email and password that alreadey registerd or added in your project */
#define USER_EMAIL "email@account.com"        
#define USER_PASSWORD "password for your account" 

/* Please adjust the Realtime Database Path (where the data store) and sampling interval */
#define RTDB_PATH "test/NodeMCU_A"
#define INTERVAL  20000    //sample interval in millseconds  (20000 = 20 seconds)

/*************************** No change needed below this line ********************************/

// Declare Firebase Data object
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

//Declare BME280 object
Adafruit_BME280 bme280;

unsigned long sendDataPrevMillis = 0;

//unsigned long count = 0;

void setup() {

  Serial.begin(115200);
  while (!Serial) {}  //wait till serial is connected
  delay(10);          //delay 10 milliseonds to make sure serial port is ready
  Serial.println("Start....");

  //connecting Wi-Fi network
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  //unsigned long ms = millis();
  int i = 0;
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(++i);
    Serial.print(' ');
    delay(300);
  }
  Serial.println("WiFi connected!!");
  Serial.print("Connected with IP: \t ");
  Serial.println(WiFi.localIP());

  char status = bme280.begin();
  while (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring, address, sensor ID!");
    Serial.print("SensorID was: 0x");
    Serial.println(bme280.sensorID(), 16);
    Serial.print("        ID of 0xFF probably means a bad address, a BMP 180 or BMP 085\n");
    Serial.print("        ID of 0x56-0x58 represents a BMP 280,\n");
    Serial.print("        ID of 0x60 represents a BME 280.\n");
    Serial.print("        ID of 0x61 represents a BME 680.\n");
    while (1) delay(10);  //stop the code here if BME280/680 is not found
  }

  Serial.printf("Firebase Client v%s\n\n", FIREBASE_CLIENT_VERSION);

  /* Assign the api key (required) */
  config.api_key = API_KEY;

  /* Assign the user sign in credentials */
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  /* Assign the RTDB URL (required) */
  config.database_url = DATABASE_URL;

  /* Assign the callback function for the long running token generation task */
  config.token_status_callback = tokenStatusCallback;  // see addons/TokenHelper.h

  // Comment or pass false value when WiFi reconnection will control by your code or third party library e.g. WiFiManager
  Firebase.reconnectNetwork(true);

  // Since v4.4.x, BearSSL engine was used, the SSL buffer need to be set.
  // Large data transmission may require larger RX buffer, otherwise connection issue or data read time out can be occurred.
  fbdo.setBSSLBufferSize(4096 /* Rx buffer size in bytes from 512 - 16384 */, 1024 /* Tx buffer size in bytes from 512 - 16384 */);

  // Limit the size of response payload in bytes to be collected in FirebaseData
  fbdo.setResponseSize(2048);

  Firebase.begin(&config, &auth);

  Firebase.setDoubleDigits(5);

  config.timeout.serverResponse = 10 * 1000;
}

void loop() {

  if (Firebase.ready() && (millis() - sendDataPrevMillis > INTERVAL || sendDataPrevMillis == 0)) {
    sendDataPrevMillis = millis();

    // For the usage of FirebaseJson, see examples/FirebaseJson/BasicUsage/Create_Edit_Parse.ino
    FirebaseJson json;

    json.set("Timestamp/.sv", F("timestamp"));
    json.set("temperature(C)", bme280.readTemperature());
    json.set("pressure(hPa)", bme280.readPressure());
    json.set("humidity(%)", bme280.readHumidity());
    json.toString(Serial);   //display the json object in Serial monitor
    Serial.println();
    Serial.printf("Push json... %s\n", Firebase.RTDB.pushJSON(&fbdo, F(RTDB_PATH), &json) ? "ok" : fbdo.errorReason().c_str());

  }
}

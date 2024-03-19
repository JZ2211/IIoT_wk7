# IIoT Workshop - week 7 
## Project: Firebase Real-time Database for IoT Applications
**System Diagram**
<img src="https://github.com/JZ2211/IIoT_wk7/assets/100505718/9bf1374d-c225-4f49-b4e3-278b73301d77" width = "600">

## NodeMCU with a BME280 sensor
1. install **Firebase Arduino Client library for ESP32 and ESP8266** in Arduino IDE
2. download example code ***firebase_client.ino*** and run the code (make sure you modify the WiFi and API key/Database URL configs at the top of the program)

## Raspberry Pi with a BME280 sensor
1. install firebase-admin package for Python: ```pip install firebase-admin```
2. code ***firebase_test.py***: Test if it can write/read data to/from firebase
3. code ***firebase_bme280.py***: push sensor data along with the date/time information to the firebase.
4. code ***savedata.py***: called by ***firebase_bme280.py*** to save data locally on Raspberry pi. 



   


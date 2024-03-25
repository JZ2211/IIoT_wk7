# Test firebase realtime database connection using firebase-admin
# Created on July 28 2023
# By Jin Zhu
# 
# required package: firebase-admin 
# $sudo pip3 install firebase-admin==5.4.0

import time
from datetime import datetime
import re
import sys
import board
from adafruit_bme280 import basic as BME280
from savedata import savedata_locally as document

#package used for firebase access
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#modify the json file name and the database URL for your firebase project
cred=credentials.Certificate('your-project-firebase.json')
firebase_admin.initialize_app(cred, {'databaseURL':'https://your-project-default-rtdb.firebaseio.com'})

#Data will be save under the dirctory HOMEPATH/nodeID locally. For example, /home/pi/node1
HOMEPATH='/home/pi/'        #adjust the home path as needed
nodeID = "sensor1"          #indicate the node ID, modify as needed
RTDB_PATH = '/test/sensor1' #under the path where the data are stored, modify as needed
TIME_INTERVAL = 10          #Sensor data are collected every TIME_INTERVAL seconds

#BME280 setup
i2cbus = board.I2C() #use default raspberry pi board SCL and SDA for I2C
mybme280=BME280.Adafruit_BME280_I2C(i2cbus,0x77)  #the default I2C address is 0x77 for adafruit BME280 board.
#use BME280(i2cbus, 0x76) instead if the I2C address is 0x76 
#data fields for BME280 sensor
datatype = "Date, Time, Temperature(C), Pressure(hPa), Humidity(%)"

currenttime=time.time() #obtain the current time
try:
     ref = db.reference(RTDB_PATH)
     print("Start reading data from BME280......\n")
     while True:
       start = currenttime
       temp = time.time()
       if (temp - start)> TIME_INTERVAL:
         currenttime = temp
         timestamp = str(datetime.now()) #obtain current time and date

         #BME280 results
         temperature = mybme280.temperature #obtain the ambient temprature in Celsius degree
         pressure = mybme280.pressure  #obtain the pressure in hPa
         humidity = mybme280.humidity  #obtain the relative humidity in percentage
         timestamp = re.sub(' ',', ', timestamp)
         output = timestamp + ", {0:.2f}, {1:.2f}, {2:.2f}".format(temperature, pressure, humidity)
         document(output, datatype)  #save data into a local text file
         tmp = timestamp.split(', ')
         rpidate = tmp[0] 
         rpitime = tmp[1]
         print(output) #display last result in the terminal
         ref.push().set({'date':rpidate, 'time':rpitime, 'Temperature (degC)': temperature, 'Humidity (%)': humidity, 'Pressure (hPa)': pressure})

except KeyboardInterrupt:
      print("Interrupted by User")
      sys.exit(0)


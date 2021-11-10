# Importing Libraries
import cv2 as cv
import paho.mqtt.client as mqtt
import base64
import time


# Raspberry PI IP address
MQTT_BROKER = 'broker.mqttdashboard.com'
# Topic on which frame will be published
MQTT_SEND = "DSR5/1"
# Object to capture the frames
cap = cv.VideoCapture(0)
# Phao-MQTT Clinet
client = mqtt.Client()
# Establishing Connection with the Broker
client.connect(MQTT_BROKER)


try:
 while True:
  start = time.time()
  # Read Frame
  _, frame = cap.read()
  # Resize Frame
  frame = cv.resize(frame, [80, 120] )
  # Encoding the Frame
  _, buffer = cv.imencode('.jpg', frame)
  # Converting into encoded bytes
  jpg_as_text = base64.b64encode(buffer)
  # Publishig the Frame on the Topic home/server
  client.publish(MQTT_SEND, jpg_as_text)
  end = time.time()
  t = end - start
  fps = 1/t
  print(fps)
  time.sleep(0.1)
except:
 cap.release()
 client.disconnect()
 print("\nNow you can restart fresh")
import time
from numpy.core.defchararray import decode
import serial
import paho.mqtt.client as mqtt
import cv2 as cv
import base64
import threading
# from seg_ref import run_cv, StoreCoor
import numpy as np

class Subscriber():
    def __init__(self, store_coor, port = None):
        self.bt_signal = False
        self.bt_msg = ""
        self.store_coor = store_coor
        
        self.port = port
        if port:
            self.ser = self.bt_connect(port)

        self.bluetooth = not(port == None)

        client = mqtt.Client()
        self.client = client
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect('broker.mqttdashboard.com', 1883, 60)
    
        def loop_infinito():
            client.loop_forever()
        t = threading.Thread(target=loop_infinito)
        t.start()

    def on_connect(self, client, userdata, flags, rc):
        print('Se conectó con MQTT ' + str(rc))
        client.subscribe('DSR5/1')

    def on_message(self, client, userdata, msg):
        decoded_msg = str(msg.payload.decode('utf-8'))
        print(msg.topic + ' ' + decoded_msg)
        if decoded_msg[:3] == "SPD":
            if self.bluetooth:
                self.bt_send(decoded_msg[3:])
        elif decoded_msg[:3] == "CAM":
            t =threading.Thread(target=self.video)
            t.start()
            pass
        elif decoded_msg[:3] == "REF":
            x,y = decoded_msg[3:].split(",")
            self.store_coor.click_event(int(float(x)),int(float(y)))
        
        elif decoded_msg[:3] == "KSA":
            list_msg = decoded_msg[3:].split('$')
            kpa = list_msg[0]
            kda = list_msg[1]
            kia = list_msg[2]
            self.bt_send(f"KSA{kpa}${kda}${kia}")

    def bt_send(self, msg):
        if not self.port:
            return
        msgOnEncode = str.encode(msg)
        self.ser.write(msgOnEncode) 
        time.sleep(1)
        self.ser.write(msgOnEncode)
        time.sleep(1)
        print(f"Mensaje enviado {msg}")

    def bt_connect(self, port):
        # seria.Serial nos permite abrir el puerto COM deseado	
        ser = serial.Serial(port, baudrate = 38400, timeout = 1)
        # Cuando se abre el puerto serial con el Arduino, este siempre se reinicia por lo que hay que esperar a que inicie para enviar los mensajes
        time.sleep(5)
        return ser

    def bt_close(self):
        self.ser.close()

    def video(self):
        # IP address
        MQTT_BROKER = 'broker.mqttdashboard.com'
        # Topic on which frame will be published
        MQTT_SEND = "DSR5/CAM"
        # Object to capture the frames
        cap = cv.VideoCapture(1)
        # Phao-MQTT Clinet
        client = mqtt.Client()
        # Establishing Connection with the Broker
        client.connect(MQTT_BROKER)
        # counter = 0
        try:
            while True:
                # start = time.time()
                # Read Frame
                _, frame = cap.read()
                # Resize Frame
                # frame = cv.resize(frame, [80, 120] )
                frame = cv.resize(frame, [160, 120] )
                # Encoding the Frame
                _, buffer = cv.imencode('.jpg', frame)
                # Converting into encoded bytes
                jpg_as_text = base64.b64encode(buffer)
                # Publishig the Frame on the Topic home/server
                client.publish(MQTT_SEND, jpg_as_text)
                # end = time.time()
                # t = end - start
                # fps = 1/t
                # print(fps)
                # print(counter)
                # counter += 1
                time.sleep(0.5)
        except:
            cap.release()
            client.disconnect()
            print("\nNow you can restart fresh")



<<<<<<< HEAD:UCPC/subscriber.py



# run_cv(store_coor, clase=sub)
=======

store_coor = StoreCoor()
sub = Subscriber(port)

run_cv(store_coor, clase=sub)
>>>>>>> 0d8389f8d3df98ebc2d51f3a1c82c6a5f30a7afc:UCPC/UCPC.py


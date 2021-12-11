import time
from numpy.core.defchararray import decode
import serial
import paho.mqtt.client as mqtt
import cv2 as cv
import base64
import threading
import numpy as np
import json
import base64
import sys
import parameters as p
import random

class Subscriber():
    def __init__(self, store_coor, port = None, fps = 10):
        self.video_id = 0
        self.auto = False
        self.mqtt_dict = dict()
        self.fps = fps
        self.current_frame = None
        self.bt_signal = False
        self.bt_msg = ""
        self.store_coor = store_coor
        self.linear_constants = [0.0, 0.0, 0.0] # kp, ki, kd
        self.angular_constants = [0.0, 0.0, 0.0] # kp, ki, kd
        
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
            self.auto = False
            if self.bluetooth:
                self.bt_send("REF" + decoded_msg[3:])
        elif decoded_msg[:3] == "CAM":
            t = threading.Thread(target=self.video)
            t.start()
            pass
        elif decoded_msg[:3] == "REF":
            x,y = decoded_msg[3:].split(",")
            self.store_coor.click_event(int(float(x)),int(float(y)))
        
        elif decoded_msg[:3] == "KSA":
            self.auto = True
            list_msg = decoded_msg[3:].split('$')
            list_msg = list(map(lambda x: float(x), list_msg))
            self.angular_constants = list_msg
            kpa = list_msg[0]
            kda = list_msg[1]
            kia = list_msg[2]
            self.bt_send(f"KSA{kpa}${kda}${kia}")
            
        elif decoded_msg[:3] == "KSL":
            self.auto = True
            list_msg = decoded_msg[3:].split('$')
            try: 
                list_msg = list(map(lambda x: float(x), list_msg))
                self.linear_constants = list_msg
            except: 
                print("Favor ingrese valores numéricos")
                print(f"Ingresado: {list_msg}")


    def bt_send(self, msg):
        if not self.port:
            return
        msgOnEncode = str.encode(msg)
        self.ser.write(msgOnEncode) 
        time.sleep(1)
        self.ser.write(msgOnEncode)
        time.sleep(1)
        print(f"Mensaje enviado {msg}")

    def bt_receive(self):
        if not self.port:
            return
        try:
            MQTT_BROKER = 'broker.mqttdashboard.com'
            MQTT_DATA = p.MQTT_ARD

            client = mqtt.Client()
            # Establishing Connection with the Broker
            client.connect(MQTT_BROKER)
            encoded_msg = self.ser.readline()
            msg = encoded_msg.decode('utf8', 'strict')
            print(f"Mensaje recibido por BT: {msg}")
            client.publish(MQTT_DATA, msg)
            # data = json.loads(msg)
            # print(f"keys: {data.keys()}")

        except Exception as e:
            print("\nError de Recepcion BT")
            print(e)

    def bt_connect(self, port):
        # seria.Serial nos permite abrir el puerto COM deseado	
        ser = serial.Serial(port, baudrate = 38400, timeout = 1)
        # Cuando se abre el puerto serial con el Arduino, este siempre se reinicia por lo que hay que esperar a que inicie para enviar los mensajes
        time.sleep(5)
        return ser

    def bt_close(self):
        self.ser.close()

    def video(self):
        this_video_id = random.randint(0, 100000)
        self.video_id = this_video_id
        # IP address
        MQTT_BROKER = 'broker.mqttdashboard.com'
        # Topic on which frame will be published
        MQTT_CAM = p.MQTT_CAM
        MQTT_DATA = p.MQTT_DATA
        # MQTT_CAM = "DSR5/CAM"
        # Object to capture the frames
        # cap = cv.VideoCapture(1)
        # Phao-MQTT Clinet
        client = mqtt.Client()
        # Establishing Connection with the Broker
        client.connect(MQTT_BROKER)
        # counter = 0
        try:
            i = 0
            while (this_video_id == self.video_id):
                if i > 300:
                # if i > 300: 

                    i = 0
                i += 1
                # start = time.time()
                # Read Frame
                # _, frame = cap.read()
                frame = self.current_frame
                
                # Resize Frame
                # frame = cv.resize(frame, [80, 120] )
                # frame = cv.resize(frame, [160, 120] )
                frame = cv.resize(frame, [320, 240] )
                
                # Encoding the Frame
                _, buffer = cv.imencode('.jpg', frame)
                # Converting into encoded bytes
                jpg_as_text = base64.b64encode(buffer)
                # Publishig the Frame on the Topic home/server
                # self.mqtt_dict['image'] = jpg_as_text
                self.mqtt_dict['indx'] = i

                # new_dict = {'x': 10, 'y': 20}
                # json_data = json.dumps(new_dict)
                # json_data = base64.b64encode(json_data)
                # print(f"Json: {json_data}")

                # MQTT_SEND = "DSR5/CAM"
                # idx = str(i).zfill(5)[-5:]
                idx_bytes = int(i).to_bytes(2,'little')
                msg = idx_bytes + jpg_as_text
                # print(f"idx: { int.from_bytes(msg[:2], 'little') }")
                client.publish(MQTT_CAM, msg)
                # print(i)


                # MQTT_SEND = "DSR5/DATA"

                json_data = json.dumps(self.mqtt_dict)
                client.publish(MQTT_DATA, json_data)

                # end = time.time()
                # t = end - start
                # fps = 1/t
                # print(fps)
                # print(counter)
                # counter += 1
                # time.sleep(0.5)
                time.sleep(1/self.fps)
        except Exception as e:
            # cap.release()
            print(f"Excepción ocurrida: {e.__class__}")
            client.disconnect()
            print("\nNow you can restart fresh")

# run_cv(store_coor, clase=sub)


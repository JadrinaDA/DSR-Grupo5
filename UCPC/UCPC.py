import time
import serial
import paho.mqtt.client as mqtt
import cv2 as cv
import base64
import threading

class Subscriber():
    def __init__(self, port = None):
        if port:
            self.ser = self.bt_connect(port)

        self.bluetooth = not(port == None)

        client = mqtt.Client()
        self.client = client
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect('broker.mqttdashboard.com', 1883, 60)
        client.loop_forever()

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

    def bt_send(self, msg):
        msgOnEncode = str.encode(msg)
        self.ser.write(msgOnEncode) 
        time.sleep(1)
        self.ser.write(msgOnEncode)
        time.sleep(1)
        print("Mensaje enviado")

    def bt_connect(self, port):
        # seria.Serial nos permite abrir el puerto COM deseado	
        ser = serial.Serial(port, baudrate = 38400, timeout = 1)
        # Cuando se abre el puerto serial con el Arduino, este siempre se reinicia por lo que hay que esperar a que inicie para enviar los mensajes
        time.sleep(5)
        return ser

    def bt_close(self):
        self.ser.close()

    def video(self):
        # Raspberry PI IP address
        MQTT_BROKER = 'broker.mqttdashboard.com'
        # Topic on which frame will be published
        MQTT_SEND = "DSR5/CAM"
        # Object to capture the frames
        cap = cv.VideoCapture(0)
        # Phao-MQTT Clinet
        client = mqtt.Client()
        # Establishing Connection with the Broker
        client.connect(MQTT_BROKER)
        try:
            while True:
                # start = time.time()
                # Read Frame
                _, frame = cap.read()
                # Resize Frame
                # frame = cv.resize(frame, [80, 120] )
                frame = cv.resize(frame, [120, 160] )
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
                time.sleep(0.1)
        except:
            cap.release()
            client.disconnect()
            print("\nNow you can restart fresh")

port = "/dev/cu.IRB-G01-SPPDev"
#port = "/dev/cu.iPhonedeIgnacio-Wireles"

sub = Subscriber(port)
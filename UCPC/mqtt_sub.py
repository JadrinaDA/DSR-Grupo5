import time
import serial
import paho.mqtt.client as mqtt

class Subscriber():
    def __init__(self, port = None):
        if port:
            self.ser = self.bt_connect(port)

        self.bluetooth = not(port == None)

        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect('broker.mqttdashboard.com', 1883, 60)
        client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print('Se conectó con MQTT ' + str(rc))
        client.subscribe('DSR5/#')

    def on_message(self, client, userdata, msg):
        decoded_msg = str(msg.payload.decode('utf-8'))
        print(msg.topic + ' ' + decoded_msg)
        if self.bluetooth:
            self.bt_send(decoded_msg)

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

port = "/dev/cu.G01-DevB"
port = "/dev/cu.iPhonedeIgnacio-Wireles"

sub = Subscriber()
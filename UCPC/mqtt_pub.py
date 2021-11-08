import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect('broker.mqttdashboard.com', 1883, 60)


def send_message(message):
    client.publish('DSR5/1', message)
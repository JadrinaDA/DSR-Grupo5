import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print('Se conectó con MQTT ' + str(rc))
    client.subscribe('DSR5/#')

def on_message(client, userdata, msg):
    print(msg.topic+' ' +str(msg.payload.decode('utf-8')))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect('broker.mqttdashboard.com', 1883, 60)
client.loop_forever()


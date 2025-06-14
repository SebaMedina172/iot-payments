import paho.mqtt.client as mqtt
import time

BROKER = "localhost"
PORT = 1883
TOPIC = "test/topic"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

# Pequeña pausa para asegurar la conexión
time.sleep(0.5)

mensaje = "¡hola desde MQTT!"
client.publish(TOPIC, mensaje)
print("Publicado:", mensaje)
client.disconnect()
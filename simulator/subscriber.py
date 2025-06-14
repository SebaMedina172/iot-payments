import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "test/topic"

def on_connect(client, userdata, flags, rc):
    print(f"🔌 Intentando conectar... Código de resultado: {rc}")
    if rc == 0:
        print("✅ ¡Conectado exitosamente al broker!")
        client.subscribe(TOPIC)
    else:
        print("❌ Fallo al conectar al broker.")

def on_message(client, userdata, msg):
    print(f"Recibido en {msg.topic}: {msg.payload.decode()}")
    # Opcional: desconectar tras recibir un mensaje para la prueba
    client.disconnect()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, PORT, 60)
    client.loop_forever()
except ConnectionRefusedError:
    print("❌ Error: No se pudo conectar al broker.")
except KeyboardInterrupt:
    print("👋 Desconectando...")
    client.disconnect()
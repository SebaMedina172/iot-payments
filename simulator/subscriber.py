import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("🔌 Suscriptor conectado, código", rc)
    if rc == 0:
        print("✅ Conexión exitosa. Suscribiéndose al topic.")
        client.subscribe("payments/requests")
    else:
        print("❌ Fallo al conectar.")

def on_message(client, userdata, msg):
    print("📩 Recibido en suscriptor:", msg.payload.decode())

def on_log(client, userdata, level, buf):
    print("📋 LOG:", buf)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log  # Activar logs de MQTT para debug

try:
    client.connect("localhost", 1883, 60)
    print("🚀 Intentando conectar al broker...")
    client.loop_forever()
except Exception as e:
    print("❌ Error de conexión:", e)

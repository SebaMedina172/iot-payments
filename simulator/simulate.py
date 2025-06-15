import paho.mqtt.client as mqtt
import json, uuid, random, time
import os

BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC = os.getenv("MQTT_TOPIC_REQ", "payments/requests")

def run_simulation(n=5, interval=1):
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    for i in range(n):
        txn = {"id": str(uuid.uuid4()), "amount": round(random.uniform(10, 200), 2)}
        client.publish(TOPIC, json.dumps(txn))
        print("Publicado:", txn)
        time.sleep(interval)
    client.disconnect()

if __name__ == "__main__":
    run_simulation(n=10, interval=0.5)

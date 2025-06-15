import os, json, time
import paho.mqtt.client as mqtt
from models import process_logic_and_update

MQTT_HOST = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
REQUEST_TOPIC = os.getenv("MQTT_TOPIC_REQ", "payments/requests")
RESPONSE_TOPIC = os.getenv("MQTT_TOPIC_RESP", "payments/responses")
MAX_RETRIES = 10
RETRY_DELAY = 2

def when_connected(client, userdata, flags, result_code):
    if result_code == 0:
        print(f"[MQTT] Conectado a {MQTT_HOST}:{MQTT_PORT}")
        client.subscribe(REQUEST_TOPIC)
        print(f"[MQTT] Escuchando en: {REQUEST_TOPIC}")
    else:
        print(f"[MQTT] Error al conectar, código {result_code}")

def when_message_arrives(client, userdata, message):
    try:
        data = json.loads(message.payload.decode())
    except Exception as error:
        print(f"[MQTT] No pude leer el JSON: {error}")
        return
    transaction_id = data.get("id")
    money_amount = data.get("amount")
    if not transaction_id or money_amount is None:
        print("[MQTT] Mensaje incompleto - falta el ID o el monto")
        return
    print(f"[MQTT] Nueva transacción: {transaction_id} por ${money_amount}")
    final_status = process_logic_and_update(transaction_id, money_amount)
    response_data = {"id": transaction_id, "status": final_status}
    client.publish(RESPONSE_TOPIC, json.dumps(response_data))
    print(f"[MQTT] Respuesta enviada a {RESPONSE_TOPIC}: {response_data}")

def run_mqtt_client():
    client = mqtt.Client()
    client.on_connect = when_connected
    client.on_message = when_message_arrives

    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            print(f"[MQTT] Intentando conectar a {MQTT_HOST}:{MQTT_PORT} (intento {attempt+1})")
            client.connect(MQTT_HOST, MQTT_PORT, 60)
            break
        except Exception as e:
            attempt += 1
            print(f"[MQTT] No se pudo conectar: {e}. Reintentando en {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
    else:
        print(f"[MQTT] No se pudo conectar tras {MAX_RETRIES} intentos.")
        return None

    client.loop_start()
    return client

if __name__ == "__main__":
    client = run_mqtt_client()
    if client:
        print("Cliente MQTT funcionando... Presiona Ctrl+C para parar.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            client.loop_stop()
            print("\n¡Cliente MQTT desconectado!")

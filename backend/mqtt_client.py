import json
import time
import paho.mqtt.client as mqtt
from config import settings
from models import process_logic_and_update

def when_connected(client, userdata, flags, result_code):
    if result_code == 0:
        print(f"[MQTT] Conectado a {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
        client.subscribe(settings.MQTT_TOPIC_REQ)
        print(f"[MQTT] Escuchando en: {settings.MQTT_TOPIC_REQ}")
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
    client.publish(settings.MQTT_TOPIC_RESP, json.dumps(response_data))
    print(f"[MQTT] Respuesta enviada a {settings.MQTT_TOPIC_RESP}: {response_data}")

def run_mqtt_client():
    client = mqtt.Client()
    client.on_connect = when_connected
    client.on_message = when_message_arrives

    attempt = 0
    while attempt < settings.MQTT_MAX_RETRIES:
        try:
            print(f"[MQTT] Intentando conectar a {settings.MQTT_BROKER}:{settings.MQTT_PORT} (intento {attempt+1})")
            client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
            break
        except Exception as e:
            attempt += 1
            print(f"[MQTT] No se pudo conectar: {e}. Reintentando en {settings.MQTT_RETRY_DELAY}s...")
            time.sleep(settings.MQTT_RETRY_DELAY)
    else:
        print(f"[MQTT] No se pudo conectar tras {settings.MQTT_MAX_RETRIES} intentos.")
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
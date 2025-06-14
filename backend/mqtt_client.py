import os
import json
import paho.mqtt.client as mqtt
from models import handle_transaction_workflow

# Configuración del broker - si no está en las variables de entorno usa localhost
MQTT_HOST = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
REQUEST_TOPIC = os.getenv("MQTT_TOPIC_REQ", "payments/requests")
RESPONSE_TOPIC = os.getenv("MQTT_TOPIC_RESP", "payments/responses")

def when_connected(client, userdata, flags, result_code):
    print(f"[MQTT] Conectado a {MQTT_HOST}:{MQTT_PORT} (código: {result_code})")
    # Suscripcion al topic de requests
    client.subscribe(REQUEST_TOPIC)
    print(f"[MQTT] Escuchando en: {REQUEST_TOPIC}")

def when_message_arrives(client, userdata, message):
    # Parsear el JSON que llegó
    try:
        data = json.loads(message.payload.decode())
    except Exception as error:
        print(f"[MQTT] No pude leer el JSON: {error}")
        return
    
    # Verificar que tenga los datos necesarios
    transaction_id = data.get("id")
    money_amount = data.get("amount")
    
    if not transaction_id or money_amount is None:
        print("[MQTT] Mensaje incompleto - falta el ID o el monto")
        return
    
    print(f"[MQTT] Nueva transacción: {transaction_id} por ${money_amount}")
    
    # Procesar la transacción
    final_status = handle_transaction_workflow(transaction_id, money_amount)
    
    # Mandamos respuesta de vuelta
    response_data = {"id": transaction_id, "status": final_status}
    client.publish(RESPONSE_TOPIC, json.dumps(response_data))
    print(f"[MQTT] Respuesta enviada a {RESPONSE_TOPIC}: {response_data}")

def run_mqtt_client():
    """Arranca el cliente MQTT y lo deja corriendo en segundo plano"""
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = when_connected
    mqtt_client.on_message = when_message_arrives
    
    mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
    mqtt_client.loop_start()
    return mqtt_client

if __name__ == "__main__":
    client = run_mqtt_client()
    print("Cliente MQTT funcionando... Presiona Ctrl+C para parar.")
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        client.loop_stop()
        print("\n¡Cliente MQTT desconectado!")
import json
import time
import paho.mqtt.client as mqtt
from config import settings
from models import process_logic_and_update

def when_connected(client, userdata, flags, result_code):
    if result_code == 0:
        print(f"[MQTT] Conectado a {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
        
        try:
            result, mid = client.subscribe(settings.MQTT_TOPIC_REQ)
            print(f"[MQTT] Intentando suscribirse a: {settings.MQTT_TOPIC_REQ}")
            print(f"[MQTT] Resultado de suscripción: {result}, Message ID: {mid}")
            if result == mqtt.MQTT_ERR_SUCCESS:
                print(f"[MQTT] ✅ Suscripción exitosa a: {settings.MQTT_TOPIC_REQ}")
            else:
                print(f"[MQTT] ❌ Error en suscripción: {result}")
        except Exception as e:
            print(f"[MQTT] ❌ Excepción al suscribirse: {e}")
    else:
        print(f"[MQTT] Error al conectar, código {result_code}")

def on_subscribe(client, userdata, mid, granted_qos):
    """Callback que se ejecuta cuando la suscripción es confirmada por el broker"""
    print(f"[MQTT] ✅ Suscripción confirmada por el broker. Message ID: {mid}, QoS: {granted_qos}")

def on_disconnect(client, userdata, rc):
    """Callback que se ejecuta cuando se desconecta del broker"""
    print(f"[MQTT] ⚠️ Desconectado del broker. Código: {rc}")

def when_message_arrives(client, userdata, message):
    print(f"[MQTT] 🔔 ¡Mensaje recibido! Topic: {message.topic}, Payload: {message.payload.decode()}")
    
    try:
        data = json.loads(message.payload.decode())
        print(f"[MQTT] 📄 JSON parseado correctamente: {data}")
    except Exception as error:
        print(f"[MQTT] ❌ No pude leer el JSON: {error}")
        return
    
    transaction_id = data.get("id")
    money_amount = data.get("amount")
    
    device_id = data.get("device_id", "unknown_device") # Añadir un valor por defecto si no viene device_id
    
    if not transaction_id or money_amount is None:
        print("[MQTT] ❌ Mensaje incompleto - falta el ID o el monto")
        return
    
    print(f"[MQTT] 🔄 Procesando transacción: {transaction_id} por ${money_amount} de {device_id}")
    
    try:
        final_status = process_logic_and_update(transaction_id, money_amount, device_id)
        print(f"[MQTT] ✅ Transacción procesada. Estado final: {final_status}")
        
        response_data = {"id": transaction_id, "status": final_status}
        client.publish(settings.MQTT_TOPIC_RESP, json.dumps(response_data))
        print(f"[MQTT] 📤 Respuesta enviada a {settings.MQTT_TOPIC_RESP}: {response_data}")
    except Exception as e:
        print(f"[MQTT] ❌ Error procesando transacción {transaction_id}: {e}")

def run_mqtt_client():
    client = mqtt.Client()
    
    # Asignar todos los callbacks
    client.on_connect = when_connected
    client.on_message = when_message_arrives
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect 

    # Configurar credenciales y TLS/SSL para HiveMQ Cloud
    print(f"[MQTT] 🔐 Configurando credenciales: Usuario={settings.MQTT_USERNAME}")
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.tls_set() # Habilitar TLS/SSL

    attempt = 0
    while attempt < settings.MQTT_MAX_RETRIES:
        try:
            print(f"[MQTT] 🔌 Intentando conectar a {settings.MQTT_BROKER}:{settings.MQTT_PORT} (intento {attempt+1})")
            client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
            break
        except Exception as e:
            attempt += 1
            print(f"[MQTT] ❌ No se pudo conectar: {e}. Reintentando en {settings.MQTT_RETRY_DELAY}s...")
            time.sleep(settings.MQTT_RETRY_DELAY)
    else:
        print(f"[MQTT] ❌ No se pudo conectar tras {settings.MQTT_MAX_RETRIES} intentos.")
        return None

    print(f"[MQTT] 🚀 Iniciando loop del cliente MQTT...")
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

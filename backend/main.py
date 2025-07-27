import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings, get_cors_origins
from models import init_db, list_transactions, process_logic_and_update
from mqtt_client import run_mqtt_client

import uuid
import random
import json
import time
import paho.mqtt.client as mqtt

app = FastAPI()

# Configuración de CORS usando la configuración centralizada
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Inicializar BD con la URL configurada
    init_db(settings.DATABASE_URL)
    print("[STARTUP] Base de datos inicializada.")
    
    # Solo iniciar cliente MQTT si no estamos en modo simulación directa
    if not settings.USE_SIMULATE_DIRECT:
        client = run_mqtt_client()
        print("[STARTUP] Cliente MQTT iniciado.")
    else:
        print("[STARTUP] Modo simulación directa activado - MQTT deshabilitado.")

@app.get("/transactions")
async def get_transactions():
    """
    Devuelve la lista de transacciones procesadas (y pendientes).
    """
    return list_transactions()

@app.delete("/transactions")
async def delete_transactions():
    """
    Borra todas las transacciones (elimina el archivo SQLite y recrea la tabla vacía).
    """
    try:
        # Extraer el path del archivo de la URL de la base de datos
        # Para SQLite, settings.DATABASE_URL es algo como "sqlite:///./transactions.db"
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        
        import os
        if os.path.exists(db_path):
            os.remove(db_path)
        
        init_db(settings.DATABASE_URL)
        return JSONResponse(content={"detail": "Transacciones borradas"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error borrando transacciones: {e}")

@app.post("/simulate")
async def simulate_transactions(
    background_tasks: BackgroundTasks,
    count: int = Query(5, ge=1, le=100),
    interval_ms: int = Query(500, ge=0, le=5000),
):
    """
    Simula 'count' transacciones publicándolas en el broker MQTT, con un intervalo en ms entre ellas.
    Se ejecuta en background para no bloquear la respuesta.
    """
    def _publish_loop(count: int, interval_ms: int):
        client = mqtt.Client()
        try:
            client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
        except Exception as e:
            print(f"[simulate] Error conectando MQTT: {e}")
            return
        
        for _ in range(count):
            txn = {
                "id": str(uuid.uuid4()), 
                "amount": round(random.uniform(10, 200), 2)
            }
            try:
                client.publish(settings.MQTT_TOPIC_REQ, json.dumps(txn))
                print(f"[simulate] Publicado: {txn}")
            except Exception as e:
                print(f"[simulate] Error publicando: {e}")
            
            if interval_ms > 0:
                time.sleep(interval_ms / 1000.0)
        
        client.disconnect()

    background_tasks.add_task(_publish_loop, count, interval_ms)
    return JSONResponse(
        content={"detail": f"Simulación iniciada: {count} transacciones"}, 
        status_code=202
    )

@app.post("/simulate-direct")
async def simulate_direct(
    count: int = Query(5, ge=1, le=100)
):
    """
    Simula 'count' transacciones procesándolas directamente sin usar MQTT.
    Para cuando haga demo en la nube.
    """
    results = []
    for _ in range(count):
        txn_id = str(uuid.uuid4())
        amount = round(random.uniform(10, 200), 2)
        status = process_logic_and_update(txn_id, amount)
        results.append({"id": txn_id, "amount": amount, "status": status})
    
    return {
        "detail": f"Procesadas {count} transacciones directamente", 
        "transactions": results
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
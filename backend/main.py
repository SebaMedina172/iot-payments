import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings, get_cors_origins
from models import init_db, list_transactions, process_logic_and_update, _get_db_connection
from mqtt_client import run_mqtt_client

import uuid
import random
import json
import time
import paho.mqtt.client as mqtt

app = FastAPI()

# Variable global para el cliente MQTT
mqtt_publisher_client = None

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
    global mqtt_publisher_client
    try:
        # Inicializar BD con la URL configurada
        init_db(settings.DATABASE_URL)
        print("[STARTUP] Base de datos inicializada.")
        
        # Solo iniciar cliente MQTT si no estamos en modo simulación directa
        if not settings.USE_SIMULATE_DIRECT:
            mqtt_publisher_client = run_mqtt_client()
            print("[STARTUP] Cliente MQTT iniciado.")
        else:
            print("[STARTUP] Modo simulación directa activado - MQTT deshabilitado.")
    except Exception as e:
        print(f"[CRITICAL ERROR] Fallo en el evento de inicio: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.on_event("shutdown")
async def shutdown_event():
    global mqtt_publisher_client
    if mqtt_publisher_client:
        print("[SHUTDOWN] Deteniendo loop del cliente MQTT y desconectando.")
        mqtt_publisher_client.loop_stop()
        mqtt_publisher_client.disconnect()
        print("[SHUTDOWN] Cliente MQTT desconectado.")

@app.get("/transactions")
async def get_transactions():
    """
    Devuelve la lista de transacciones procesadas (y pendientes).
    """
    return list_transactions()

@app.get("/health")
async def health_check():
    """
    Health check endpoint para mantener el servicio activo.
    También hace una query simple a la base de datos para mantener Supabase activo.
    """
    try:
        # Hacer una query simple a la base de datos para mantenerla activa
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")  # Query simple
        cursor.close()
        conn.close()
        
        return JSONResponse(
            content={
                "status": "healthy",
                "database": "connected",
                "timestamp": time.time()
            }, 
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "unhealthy",
                "database": "error",
                "error": str(e),
                "timestamp": time.time()
            }, 
            status_code=503
        )

@app.get("/")
async def root():
    """
    Root endpoint para verificar que el servicio está corriendo.
    """
    return {"message": "GreenAdvice API is running", "status": "ok"}

@app.delete("/transactions")
async def delete_transactions():
    """
    Borra todas las transacciones de la tabla PostgreSQL.
    """
    conn = None
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE public.transactions RESTART IDENTITY;")
        conn.commit()
        return JSONResponse(content={"detail": "Transacciones borradas"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error borrando transacciones: {e}")
    finally:
        if conn:
            conn.close()

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
    global mqtt_publisher_client
    if not mqtt_publisher_client:
        raise HTTPException(status_code=500, detail="Cliente MQTT no inicializado. Asegúrate de que USE_SIMULATE_DIRECT no esté activado.")

    def _publish_loop(count: int, interval_ms: int):
        global mqtt_publisher_client
        
        for _ in range(count):
            txn = {
                "id": str(uuid.uuid4()), 
                "amount": round(random.uniform(10, 200), 2),
                "device_id": f"simulated_device_{random.randint(1, 10)}"
            }
            try:
                mqtt_publisher_client.publish(settings.MQTT_TOPIC_REQ, json.dumps(txn))
                print(f"[simulate] Publicado: {txn}")
            except Exception as e:
                print(f"[simulate] Error publicando: {e}")
            
            if interval_ms > 0:
                time.sleep(interval_ms / 1000.0)
        
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
    for i in range(count):
        txn_id = str(uuid.uuid4())
        amount = round(random.uniform(10, 200), 2)
        device_id = f"device-{i+1}"
        status = process_logic_and_update(txn_id, amount, device_id)
        results.append({"id": txn_id, "amount": amount, "status": status, "device_id": device_id})
    
    return {
        "detail": f"Procesadas {count} transacciones directamente", 
        "transactions": results
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)

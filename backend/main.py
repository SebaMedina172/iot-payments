import os
import uvicorn
from fastapi import FastAPI
from models import init_db, list_transactions
from mqtt_client import start_mqtt_loop

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Inicializar BD
    init_db()
    print("[STARTUP] Base de datos inicializada.")
    # Iniciar cliente MQTT en segundo plano
    client = start_mqtt_loop()
    print("[STARTUP] Cliente MQTT iniciado.")

@app.get("/transactions")
async def get_transactions():
    """
    Devuelve la lista de transacciones: procesadas y pendientes.
    """
    return list_transactions()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)

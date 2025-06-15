import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from models import init_db, list_transactions
from mqtt_client import run_mqtt_client

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Puerto donde corre Vite
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Inicializar BD
    init_db()
    print("[STARTUP] Base de datos inicializada.")
    # Iniciar cliente MQTT en background
    client = run_mqtt_client()
    print("[STARTUP] Cliente MQTT iniciado.")

@app.get("/transactions")
async def get_transactions():
    """
    Devuelve la lista de transacciones procesadas (y pendientes).
    """
    return list_transactions()

if __name__ == "__main__":
    # Uvicorn recargará cambios de código
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Feature flags
    USE_SIMULATE_DIRECT: bool = False
    
    # MQTT configuration
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_TOPIC_REQ: str = "payments/requests"
    MQTT_TOPIC_RESP: str = "payments/responses"
    MQTT_MAX_RETRIES: int = 10
    MQTT_RETRY_DELAY: int = 2
    
    # Frontend URL for CORS
    FRONTEND_URL: Optional[str] = None
    
    # Database configuration
    DATABASE_URL: str
    
    # CORS origins (hardcoded ones will be combined with FRONTEND_URL)
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Frontend contenedorizado en Docker Compose
        "http://front:80",        # Comunicación interna entre contenedores
        "https://iot-payments.vercel.app/"  # URL publica del front en Vercel
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()

def get_cors_origins() -> List[str]:
    """
    Retorna la lista completa de orígenes CORS permitidos,
    incluyendo FRONTEND_URL si está configurada.
    """
    origins = settings.CORS_ORIGINS.copy()
    if settings.FRONTEND_URL:
        origins.append(settings.FRONTEND_URL)
    return origins
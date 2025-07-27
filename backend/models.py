import psycopg2
import threading
import time
import uuid # Necesario para generar UUIDs si no usas SERIAL

# Lock para asegurar acceso thread-safe a la base de datos
# Aunque psycopg2 es thread-safe, el lock puede ser útil para operaciones de conexión/desconexión
_lock = threading.Lock()

# Variable global para almacenar la cadena de conexión
_db_url = None

def init_db(database_url: str):
    """
    Inicializa la base de datos creando la tabla 'transactions' si no existe.
    """
    global _db_url
    _db_url = database_url
    
    with _lock:
        conn = None
        try:
            conn = psycopg2.connect(_db_url)
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS public.transactions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                device_id TEXT NOT NULL,
                amount NUMERIC(10, 2) NOT NULL,
                status TEXT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                location TEXT
            );
            """)
            conn.commit()
            print("[DB] Tabla 'transactions' verificada/creada.")
        except Exception as e:
            print(f"[DB ERROR] No se pudo inicializar la base de datos: {e}")
            raise
        finally:
            if conn:
                conn.close()

def _get_db_connection():
    """
    Retorna una nueva conexión a la base de datos.
    Lanza una excepción si la DB no ha sido inicializada.
    """
    if _db_url is None:
        raise RuntimeError("La base de datos debe ser inicializada primero con init_db()")
    return psycopg2.connect(_db_url)

def save_transaction(txn_id: str, amount: float, device_id: str): # Añadir device_id
    """
    Guarda una nueva transacción en la base de datos con estado 'pending'
    """
    with _lock:
        conn = None
        try:
            conn = _get_db_connection()
            cursor = conn.cursor()
            # Incluir device_id en el INSERT
            cursor.execute(
                """
                INSERT INTO public.transactions (id, amount, status, device_id) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (txn_id, amount, "pending", device_id) # Pasar device_id aquí
            )
            conn.commit()
        except Exception as e:
            print(f"[DB ERROR] No se pudo guardar la transacción {txn_id}: {e}")
            raise
        finally:
            if conn:
                conn.close()

def update_status(txn_id: str, status: str):
    """
    Actualiza el estado de una transacción existente
    """
    with _lock:
        conn = None
        try:
            conn = _get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE public.transactions SET status = %s WHERE id = %s",
                (status, txn_id)
            )
            conn.commit()
        except Exception as e:
            print(f"[DB ERROR] No se pudo actualizar el estado de {txn_id}: {e}")
            raise
        finally:
            if conn:
                conn.close()

def process_logic_and_update(txn_id: str, amount: float, device_id: str) -> str: # Añadir device_id
    """
    Procesa una transacción aplicando lógica y actualizando su estado
    """
    # Paso 1: Guardar transacción como 'pending'
    save_transaction(txn_id, amount, device_id) # Pasar device_id aquí
    
    # Paso 2: Simular tiempo de procesamiento
    time.sleep(0.2)
    
    # Paso 3: Aplicar lógica de negocio simple
    status = "approved" if amount < 100 else "rejected"
    
    # Paso 4: Actualizar estado final
    update_status(txn_id, status)
    
    return status

def list_transactions():
    """
    Obtiene todas las transacciones ordenadas por fecha (más recientes primero)
    """
    with _lock:
        conn = None
        try:
            conn = _get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, amount, status, timestamp, location, device_id FROM public.transactions ORDER BY timestamp DESC") # Añadir device_id a la selección
            rows = cursor.fetchall()
        except Exception as e:
            print(f"[DB ERROR] No se pudieron listar las transacciones: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    # Convertir tuplas a diccionarios para facilitar el uso
    result = []
    for r in rows:
        result.append({
            "id": str(r[0]),
            "amount": float(r[1]),
            "status": r[2],
            "timestamp": r[3].isoformat(),
            "location": r[4],
            "device_id": r[5] # Añadir device_id al diccionario de resultado
        })
    
    return result

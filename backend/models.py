import sqlite3
import threading
import time

# Ruta del archivo de base de datos SQLite
DB_PATH = "transactions.db"

# Lock para asegurar acceso thread-safe a la base de datos
_lock = threading.Lock()

def init_db():
    """
    Inicializa la base de datos creando la tabla 'transactions' si no existe
    """
    with _lock:  # Asegura acceso exclusivo durante la inicialización
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            amount REAL,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        conn.close()

def save_transaction(txn_id: str, amount: float):
    """
    Guarda una nueva transacción en la base de datos con estado 'pending'
    """
    with _lock:  # Protege la operación de escritura
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO transactions (id, amount, status) VALUES (?, ?, ?)",
            (txn_id, amount, "pending")
        )
        conn.commit()
        conn.close()

def update_status(txn_id: str, status: str):
    """
    Actualiza el estado de una transacción existente
    """
    with _lock:  # Protege la operación de actualización
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE transactions SET status = ? WHERE id = ?",
            (status, txn_id)
        )
        conn.commit()
        conn.close()

def process_logic_and_update(txn_id: str, amount: float) -> str:
    """
    Procesa una transacción aplicando lógica y actualizando su estado
    """
    # Paso 1: Guardar transacción como 'pending'
    save_transaction(txn_id, amount)
    
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
    with _lock:  # Protege la operación de lectura
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Ordenar por timestamp DESC para mostrar las más recientes primero
        cursor.execute("SELECT id, amount, status, timestamp FROM transactions ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
    
    # Convertir tuplas de SQLite a diccionarios para facilitar el uso
    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "amount": r[1],
            "status": r[2],
            "timestamp": r[3]
        })
    
    return result
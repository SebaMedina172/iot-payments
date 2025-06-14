import sqlite3
import threading
import time
from datetime import datetime

# Base de datos 
DATABASE_FILE = "transactions.db"
db_lock = threading.Lock()

def setup_database():
    """Inicialia la BD - crea la tabla si no existe"""
    with db_lock:
        connection = sqlite3.connect(DATABASE_FILE)
        c = connection.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            amount REAL,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        connection.commit()
        connection.close()

def add_new_transaction(transaction_id: str, money_amount: float):
    """Genera nueva transacción como pendiente (si todavia no existe)"""
    with db_lock:
        connection = sqlite3.connect(DATABASE_FILE)
        c = connection.cursor()
        c.execute(
            "INSERT OR IGNORE INTO transactions (id, amount, status) VALUES (?, ?, ?)",
            (transaction_id, money_amount, "pending")
        )
        connection.commit()
        connection.close()

def change_transaction_status(transaction_id: str, new_status: str):
    """Cambia el estado de una transacción que ya existe"""
    with db_lock:
        connection = sqlite3.connect(DATABASE_FILE)
        c = connection.cursor()
        c.execute(
            "UPDATE transactions SET status = ? WHERE id = ?",
            (new_status, transaction_id)
        )
        connection.commit()
        connection.close()

def handle_transaction_workflow(transaction_id: str, money_amount: float) -> str:
    """
    Lógica principal: si es menos de 100 se aprueba, 
    sino se rechaza. Primero la guarda como pendiente y después actualiza.
    """
    add_new_transaction(transaction_id, money_amount)
    
    # Delay para simular procesamiento
    time.sleep(0.2)
    
    # Lógica simple: menos de 100 = ok, más = no
    final_status = "approved" if money_amount < 100 else "rejected"
    change_transaction_status(transaction_id, final_status)
    
    return final_status

def get_all_transactions():
    """Trae todas las transacciones, las más nuevas primero"""
    with db_lock:
        connection = sqlite3.connect(DATABASE_FILE)
        c = connection.cursor()
        c.execute("SELECT id, amount, status, timestamp FROM transactions ORDER BY timestamp DESC")
        all_rows = c.fetchall()
        connection.close()
    
    # Armamos una lista más fácil 
    transactions_list = []
    for row in all_rows:
        # row[3] tiene el timestamp como string tipo '2025-06-14 18:00:00'
        transactions_list.append({
            "id": row[0],
            "amount": row[1],
            "status": row[2],
            "timestamp": row[3]
        })
    
    return transactions_list
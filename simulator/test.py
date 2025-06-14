import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 1883))

if result == 0:
    print("✅ Conexión al puerto 1883 exitosa")
else:
    print("❌ No se pudo conectar al puerto 1883")

sock.close()

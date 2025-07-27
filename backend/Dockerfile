FROM python:3.11-slim

WORKDIR /app

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Variables de entorno por defecto (se pueden sobrescribir en ACA)
ENV HOST=0.0.0.0
ENV PORT=8000
ENV USE_SIMULATE_DIRECT=true
ENV DATABASE_URL=sqlite:///./data/transactions.db

# Crear directorio para la base de datos
RUN mkdir -p /app/data

# Exponer puerto
EXPOSE 8000

CMD ["python", "main.py"]
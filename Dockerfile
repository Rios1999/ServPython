FROM python:3.11-slim

WORKDIR /app

# Copiamos los archivos de requerimientos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código (la carpeta app)
COPY . .

# IMPORTANTE: Northflank asigna un puerto dinámico mediante la variable $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
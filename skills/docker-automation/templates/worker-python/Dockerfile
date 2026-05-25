FROM python:3.12-alpine

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do worker
COPY worker.py .

# Comando padrão
CMD ["python", "/app/worker.py"]

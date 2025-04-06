# Base image con Python y soporte para ODBC
FROM python:3.10-slim

# 1. Instala dependencias del sistema y el driver ODBC
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    odbcinst \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# 2. Configura el entorno
WORKDIR /app
COPY . .

# 3. Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# 4. Puerto expuesto
EXPOSE 5000

# 5. Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
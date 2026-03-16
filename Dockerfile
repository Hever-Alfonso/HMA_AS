# Usa una imagen oficial de Python ligera como base
FROM python:3.11-slim

# Establece variables de entorno para que Python no escriba archivos .pyc y la salida se muestre sin buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependencias del sistema necesarias para compilar paquetes como psycopg2 y Pillow
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia e instala los requerimientos
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn psycopg2-binary

# Copia el código completo del proyecto al contenedor
COPY . /app/

# Expone el puerto donde se ejecutará la aplicación
EXPOSE 8000

# Añade un script de inicio o un comando base
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "HMA_AS.wsgi:application"]

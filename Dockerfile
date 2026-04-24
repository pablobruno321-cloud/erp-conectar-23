# Usar imagen oficial de Python
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "--timeout", "60", "run:app"]

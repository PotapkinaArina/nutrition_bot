FROM python:3.13.9-slim 

WORKDIR /app    # установим зависимости для системы.
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .    #копируем зависимости.
RUN pip install --no-cache-dir -r requirements.txt


#запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
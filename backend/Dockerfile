FROM python:3.9-slim

WORKDIR /app

# Копируем только зависимости — это ускоряет пересборку
COPY requirements.txt .
ENV PYTHONPATH=/app


RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY .. .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

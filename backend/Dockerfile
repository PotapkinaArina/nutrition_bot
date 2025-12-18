FROM python:3.9-slim

# Рабочая директория
WORKDIR /app

# Копируем только зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код из текущей папки (backend) внутрь контейнера
COPY . .

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app

# Запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

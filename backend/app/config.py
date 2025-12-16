import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Подключение к базе данных
DATABASE_URL = os.getenv("DATABASE_URL")

# YandexGPT
YANDEX_GPT_API_KEY = os.getenv("YANDEX_GPT_API_KEY")
YANDEX_GPT_URL = os.getenv("YANDEX_GPT_URL")

import os

from dotenv import load_dotenv

load_dotenv()  # 👈 ВАЖНО

# === YandexGPT ===
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

# Можно переопределить через .env, но есть дефолт
YANDEX_GPT_URL = os.getenv(
    "YANDEX_GPT_URL",
    "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
)

# === Database ===
DATABASE_URL = os.getenv("DATABASE_URL")

# === Проверки при старте приложения ===
if not YANDEX_API_KEY:
    raise RuntimeError("❌ YANDEX_API_KEY is not set")

if not YANDEX_FOLDER_ID:
    raise RuntimeError("❌ YANDEX_FOLDER_ID is not set")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL is not set")

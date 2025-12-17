import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
YANDEX_GPT_API_KEY = os.getenv("YANDEX_GPT_API_KEY")
YANDEX_GPT_URL = os.getenv("YANDEX_GPT_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

import requests
from app.config import YANDEX_GPT_API_KEY, YANDEX_GPT_URL

SYSTEM_PROMPT = (
    "Ты — нутрициолог. Проанализируй рацион пользователя. "
    "Верни СТРОГО JSON со следующими полями: "
    "calories (int), proteins (int), fats (int), carbs (int), "
    "deficiencies (string), recommendations (string). "
    "Без текста вне JSON."
)

def analyze_text(text: str) -> str:
    return '{"calories":420,"proteins":18,"fats":12,"carbs":60,"deficiencies":"Недостаток клетчатки","recommendations":"Добавьте овощи и цельнозерновые продукты"}'



    resp = requests.post(YANDEX_GPT_URL, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()

    # предполагаем, что текст ответа — JSON-строка
    result_text = resp.json()["result"]["alternatives"][0]["message"]["text"]
    return result_text

import requests
import json
import re
from app.config import YANDEX_API_KEY, YANDEX_FOLDER_ID, YANDEX_GPT_URL

SYSTEM_PROMPT = """
Ты — нутрициолог.
Проанализируй описание еды.
Верни ТОЛЬКО JSON строго в формате:

{
  "calories": number,
  "proteins": number,
  "fats": number,
  "carbs": number,
  "deficiencies": string,
  "recommendations": string
}
"""

HEADERS = {
    "Authorization": f"Api-Key {YANDEX_API_KEY}",
    "Content-Type": "application/json"
}

def parse_gpt_response(text: str) -> dict:
    """
    Преобразует текст GPT в словарь Python, игнорируя лишние символы.
    """
    try:
        # Ищем первый {...} в ответе GPT
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("❌ JSON не найден в ответе GPT")
        json_text = match.group(0)
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        print("❌ Ошибка JSON:", e)
        return {
            "calories": None,
            "proteins": None,
            "fats": None,
            "carbs": None,
            "deficiencies": None,
            "recommendations": None
        }

def analyze_text(user_text: str) -> dict:
    """
    Отправляет текст на YandexGPT и возвращает словарь с анализом питания.
    """
    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.2,
            "maxTokens": 500
        },
        "messages": [
            {"role": "system", "text": SYSTEM_PROMPT},
            {"role": "user", "text": user_text}
        ]
    }

    try:
        response = requests.post(YANDEX_GPT_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Берём текст ответа GPT
        raw_text = data["result"]["alternatives"][0]["message"]["text"]

        # Преобразуем в словарь Python
        return parse_gpt_response(raw_text)

    except (requests.RequestException, KeyError, ValueError) as e:
        print("❌ Ошибка при запросе к YandexGPT:", e)
        return {
            "calories": None,
            "proteins": None,
            "fats": None,
            "carbs": None,
            "deficiencies": None,
            "recommendations": None
        }

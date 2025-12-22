import requests
import json
import re
from app.config import YANDEX_API_KEY, YANDEX_FOLDER_ID, YANDEX_GPT_URL

SYSTEM_PROMPT = """
Ты — профессиональный нутрициолог. Проанализируй описание приема пищи и верни JSON строго в следующем формате:

{
  "summary": "краткая сводка анализа на русском (2-3 предложения)",
  "calories": число_целое,
  "macros": {
    "protein": число_с_плавающей_точкой,
    "fat": число_с_плавающей_точкой,
    "carbs": число_с_плавающей_точкой
  },
  "deficiencies": [
    {
      "name": "название дефицита (например: белок, железо, витамин D)",
      "severity": "low/medium/high",
      "confidence": число_от_0_до_1
    }
  ],
  "recommendations": [
    "первая рекомендация",
    "вторая рекомендация",
    "третья рекомендация"
  ]
}

Правила:
1. Если не уверен в каком-то значении - ставь null
2. Максимум 3 дефицита и 5 рекомендаций
3. Дефициты указывай только если уверенность > 0.5
4. Все тексты на русском языке
5. Калории в ккал, макроэлементы в граммах
"""


HEADERS = {
    "Authorization": f"Api-Key {YANDEX_API_KEY}",
    "Content-Type": "application/json"
}


def parse_gpt_response(text: str) -> dict:
    """
    Преобразует текст GPT в словарь Python, соответствующий формату бота
    """
    try:
        # Ищем JSON в ответе
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("❌ JSON не найден в ответе GPT")

        json_text = match.group(0)
        data = json.loads(json_text)

        # Валидация и преобразование в нужный формат
        result = {
            "summary": data.get("summary", "Не удалось сгенерировать сводку"),
            "calories": data.get("calories"),
            "macros": data.get("macros", {}),
            "deficiencies": data.get("deficiencies", []),
            "recommendations": data.get("recommendations", [])
        }

        # Гарантируем структуру macros
        if "macros" not in data:
            result["macros"] = {
                "protein": data.get("proteins"),
                "fat": data.get("fats"),
                "carbs": data.get("carbs")
            }

        # Гарантируем, что deficiencies и recommendations - списки
        if isinstance(result["deficiencies"], str):
            result["deficiencies"] = [{"name": result["deficiencies"], "severity": "medium", "confidence": 0.7}]
        elif not isinstance(result["deficiencies"], list):
            result["deficiencies"] = []

        if isinstance(result["recommendations"], str):
            # Разделяем строку рекомендаций на список
            recommendations = result["recommendations"].split('.')
            result["recommendations"] = [rec.strip() for rec in recommendations if rec.strip()]
        elif not isinstance(result["recommendations"], list):
            result["recommendations"] = []

        return result

    except json.JSONDecodeError as e:
        print("❌ Ошибка парсинга JSON:", e)
        return {
            "summary": "Ошибка анализа. Попробуйте описать прием пищи подробнее.",
            "calories": None,
            "macros": {"protein": None, "fat": None, "carbs": None},
            "deficiencies": [],
            "recommendations": ["Опишите прием пищи более подробно для точного анализа"]
        }
    except Exception as e:
        print("❌ Неожиданная ошибка:", e)
        return {
            "summary": "Произошла ошибка при анализе",
            "calories": None,
            "macros": {"protein": None, "fat": None, "carbs": None},
            "deficiencies": [],
            "recommendations": ["Попробуйте еще раз или обратитесь в поддержку"]
        }


def analyze_text(user_text: str, analyze_calories: bool = True, analyze_nutrients: bool = True) -> dict:
    """
    Отправляет текст на YandexGPT и возвращает словарь с анализом питания.
    """
    # Модифицируем промпт в зависимости от флагов
    dynamic_prompt = SYSTEM_PROMPT

    if not analyze_calories:
        dynamic_prompt += "\n\nВАЖНО: Не анализируй калории, установи calories: null"
    if not analyze_nutrients:
        dynamic_prompt += "\n\nВАЖНО: Не анализируй макроэлементы, установи macros: null"

    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.1,  # Уменьшаем для большей консистентности JSON
            "maxTokens": 1000  # Увеличиваем для сложных анализов
        },
        "messages": [
            {"role": "system", "text": dynamic_prompt},
            {"role": "user", "text": f"Проанализируй этот прием пищи: {user_text}"}
        ]
    }

    try:
        response = requests.post(YANDEX_GPT_URL, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        raw_text = data["result"]["alternatives"][0]["message"]["text"]
        print("🧠 GPT RAW RESPONSE:\n", raw_text)

        return parse_gpt_response(raw_text)

    except requests.RequestException as e:
        print("❌ Ошибка при запросе к YandexGPT:", e)
        return {
            "summary": "Сервис анализа временно недоступен",
            "calories": None,
            "macros": {"protein": None, "fat": None, "carbs": None},
            "deficiencies": [],
            "recommendations": ["Попробуйте позже или опишите прием пищи текстом"]
        }


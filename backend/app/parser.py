import json

REQUIRED_FIELDS = [
    "calories", "proteins", "fats", "carbs",
    "deficiencies", "recommendations"
]

def parse_gpt_response(raw_text: str) -> dict:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        raise ValueError("GPT response is not valid JSON")

    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValueError(f"Missing field in GPT response: {field}")

    return data

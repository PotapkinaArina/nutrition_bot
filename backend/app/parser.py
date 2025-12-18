import json

def parse_gpt_response(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("GPT вернул невалидный JSON")

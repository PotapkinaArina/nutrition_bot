from app.gpt_client import analyze_text
from app.parser import parse_gpt_response

text = "Овсянка с бананом"

raw = analyze_text(text)
print("RAW:", raw)

parsed = parse_gpt_response(raw)
print("PARSED:", parsed)

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import AnalyzeRequest, AnalyzeResult
from app.deps import get_db
from app.gpt_client import analyze_text
from app.parser import parse_gpt_response

app = FastAPI(title="Nutrition Tracker API")

@app.post("/analyze", response_model=AnalyzeResult)
def analyze(req: AnalyzeRequest, db: Session = Depends(get_db)):
    try:
        raw_text = analyze_text(req.text)           # МОК или реальный GPT
        print("RAW_TEXT:", raw_text)                # <-- логируем
        parsed = parse_gpt_response(raw_text)
        print("PARSED:", parsed)                    # <-- логируем
        # Здесь можно сохранять в БД, если нужно
        return parsed
    except Exception as e:
        print("ERROR:", e)                          # <-- логируем
        raise HTTPException(status_code=500, detail=str(e))


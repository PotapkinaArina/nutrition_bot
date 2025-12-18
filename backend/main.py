from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import Base, AnalysisRequest, ParsedResult
from app.gpt_client import analyze_text

# Создаём таблицы при старте (если ещё не созданы)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nutrition Tracker API")

# Pydantic модель для запроса
class AnalyzeRequest(BaseModel):
    user_id: str
    text: str

# POST /analyze
@app.post("/analyze")
def analyze(request: AnalyzeRequest, db: Session = Depends(get_db)):
    try:
        # 1️⃣ Отправляем текст в GPT
        result = analyze_text(request.text)

        # 2️⃣ Сохраняем исходный запрос
        analysis_req = AnalysisRequest(user_id=request.user_id, text=request.text)
        db.add(analysis_req)
        db.commit()
        db.refresh(analysis_req)

        # 3️⃣ Сохраняем распарсенный результат
        parsed = ParsedResult(
            analysis_request_id=analysis_req.id,
            calories=result.get("calories"),
            proteins=result.get("proteins"),
            fats=result.get("fats"),
            carbs=result.get("carbs"),
            deficiencies=result.get("deficiencies"),
            recommendations=result.get("recommendations")
        )
        db.add(parsed)
        db.commit()

        # 4️⃣ Возвращаем результат пользователю
        return result

    except Exception as e:
        print("❌ Ошибка /analyze:", e)
        raise HTTPException(status_code=500, detail="Ошибка при обработке запроса")

# GET /history?user_id=...
@app.get("/history")
def history(user_id: str, db: Session = Depends(get_db)):
    try:
        records = db.query(ParsedResult).join(AnalysisRequest).filter(AnalysisRequest.user_id == user_id).all()
        return [
            {
                "text": r.analysis_request.text,
                "calories": r.calories,
                "proteins": r.proteins,
                "fats": r.fats,
                "carbs": r.carbs,
                "deficiencies": r.deficiencies,
                "recommendations": r.recommendations
            }
            for r in records
        ]
    except Exception as e:
        print("❌ Ошибка /history:", e)
        raise HTTPException(status_code=500, detail="Ошибка при получении истории")

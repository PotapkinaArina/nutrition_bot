from fastapi import FastAPI, HTTPException
from app.schemas import AnalyzeRequestSchema, AnalyzeResponseSchema
from app.gpt_client import analyze_text

# from app.database import get_db
# from app.models import AnalysisRequest, ParsedResult
# from sqlalchemy.orm import Session

app = FastAPI()

@app.post("/analyze", response_model=AnalyzeResponseSchema)
def analyze(request: AnalyzeRequestSchema):  # db: Session = Depends(get_db)
    try:
        # 1️⃣ Отправляем текст в GPT
        result = analyze_text(request.text)

        # 2️⃣ Временно закомментируем работу с БД
        """
        # Сохраняем исходный запрос
        analysis_req = AnalysisRequest(user_id=request.user_id, text=request.text)
        db.add(analysis_req)
        db.commit()
        db.refresh(analysis_req)

        # Сохраняем распарсенный результат
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
        """

        # 3️⃣ Возвращаем результат пользователю
        return result

    except Exception as e:
        print("❌ Ошибка при обработке запроса:", e)
        raise HTTPException(status_code=500, detail="Ошибка при обработке запроса")

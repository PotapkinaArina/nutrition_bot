from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Nutrition Bot",
    description="API для анализа питания и отслеживания нутриентов",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["htttp://localhost:8501","http://frontend:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FoodItem(BaseModel):  #(Пидантик) модели данных.
    name: str
    quantity: Optional[str]= "1 portion" 
    

class AnalysisRequest(BaseModel):
    text: str
    user_id: Optional[int] = None
    source: str = "web"

class Deficiency(BaseModel):
    name: str
    severity: str
    recommended_food: str

class AnalysisResponse(BaseModel):
    request_id: int
    calories: int
    protein: float
    fat: float
    carbs: float
    deficiencies: List[Deficiency]
    recommendations: str

class UserCreate(BaseModel):
    telegram_id: Optional[int] = None
    username: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None

class Database:
    @staticmethod
    def save_request(user_id: int,text: str, source: str)->int:
        return 1
    @staticmethod
    def save_analysis_result(request_id: int, alalysis_data: dict):
        pass
    @staticmethod
    def get_user_history(user_id: int):
        return [
            {
                "id": 1,
                "date": "овсянка, яблоко, курица",
                "calories": 450,
                "protein": 35.2,
                "fat": 12.5,
                "carbs": 55.3
            },
            {
                "id": 2,
                "date": "2024-01-14",
                "text": "гречка, говядина, салат",
                "calories": 520,
                "protein": 42.1,
                "fat":18.3,
                "carbs": 48.7
            }
        ]

db = Database()

def analyze_nutrition(text: str)->dict:
    "" "заглукшка для анализа(тут должен был быть ЯндексДЖПТ)"""
    text_lower = text.lower()

    calories = 400
    protein = 25.0
    fat = 15.0
    carbs = 50.0

    deficiencies = []

    if any(word in text_lower for word in ["молоко", "сыр", "творог", "йогурт"]):
        deficiencies.append({
            "name": "Vitanin D",
            "severity": "низкий",
            "recommended_food": "скумбрия, авокадо, солнечные ванны"
        })

     if any(word in text_lower for word in ["яблоко", "апельсин", "банан"]):
        deficiencies.append({
            "name": "Витамин C",
            "severity": "умеренный",
            "recommended_food": "цитрусовые, киви, болгарский перец"
        }) 
        if not any(word in text_lower for word in ["рыба", "лосось", "скумбрия", "тунец"]):
        deficiencies.append({
            "name": "Омега-3",
            "severity": "высокий",
            "recommended_food": "жирная рыба, грецкие орехи, льняное семя"
        })
    recommendations = "Ешьте больше овощей и цельнозерновых продуктов."

    return {
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs;
        "deficiencies": deficiencies,
        "recommendations": recommendations
    }

@app.get("/")
async def root():
    return {
        "message": "Nutrition Bot API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "POST/analyze",
            "history": "GET/history/{user_id}",
            "health": "GET/health"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyse_food(request: AnalysisRequest):
    """Анализ введённых продуктов"""
    try:
        request_id = db.save_request(request.user_id or 1, request.text, request.source)
        analysis_result = analyze_nutrition(request.text)
        db.save_analysis_result(request_id, analysis_result)

        return AnalysisResponse(
            request_id = request_id,
            calories= analysis_result["calories"],
            protein=analysis_result["protein"],
            fat=analysis_result["fat"],
            carbs=analysis_result["carbs"],
            deficiencies=analysis_result["deficiencies"],
            recommendations= analysis_result["recommendations"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/history/{user_id}")
async def get_history(user_id: int):
    """Получение истории анализов пользователя"""
    try:
        history=db.get_user_history(user_id)
        return{
            "user_id": user_id,
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/user")
async def create_user(user: UserCreate):
    """Создание/обновление пользователя"""
    return {
        "message": "User was created/updated successfully",
        "user_id": 1,
        "telegram_id": user.telegram_id,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host= "0.0.0.0", port = 8000) 
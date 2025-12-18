from typing import Optional
from pydantic import BaseModel

# Схема запроса
class AnalyzeRequestSchema(BaseModel):
    user_id: str
    text: str

# Схема ответа
class AnalyzeResponseSchema(BaseModel):
    calories: Optional[int]
    proteins: Optional[float]
    fats: Optional[float]
    carbs: Optional[float]
    deficiencies: Optional[str]
    recommendations: Optional[str]

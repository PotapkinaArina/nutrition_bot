from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class MacrosSchema(BaseModel):
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbs: Optional[float] = None

class DeficiencySchema(BaseModel):
    name: str
    severity: str  # "low", "medium", "high"
    confidence: Optional[float] = None

class AnalyzeResponseDataSchema(BaseModel):
    summary: str
    calories: Optional[int] = None
    macros: Optional[MacrosSchema] = None
    deficiencies: List[DeficiencySchema] = []
    recommendations: List[str] = []

class AnalyzeResponseSchema(BaseModel):
    status: str  # "success" или "error"
    data: Optional[AnalyzeResponseDataSchema] = None
    detail: Optional[str] = None

class AnalyzeRequestSchema(BaseModel):
    user_id: str
    text: str
    source: Optional[str] = "telegram"
    telegram_id: Optional[int] = None
    analyze_calories: Optional[bool] = True
    analyze_nutrients: Optional[bool] = True

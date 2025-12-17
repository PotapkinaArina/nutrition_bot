from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AnalyzeRequest(BaseModel):
    user_id: str
    text: str

class AnalyzeResult(BaseModel):
    calories: Optional[int]
    proteins: Optional[int]
    fats: Optional[int]
    carbs: Optional[int]
    deficiencies: Optional[str]
    recommendations: Optional[str]

class HistoryItem(BaseModel):
    created_at: datetime
    input_text: str
    result: AnalyzeResult

class HistoryResponse(BaseModel):
    user_id: str
    history: List[HistoryItem]

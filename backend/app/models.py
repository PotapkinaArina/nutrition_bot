from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    analyses = relationship("AnalysisRequest", back_populates="user")

class AnalysisRequest(Base):
    __tablename__ = "analysis_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_text = Column(Text, nullable=False)
    raw_response = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="analyses")
    parsed_result = relationship(
        "ParsedResult",
        back_populates="analysis",
        uselist=False
    )

class ParsedResult(Base):
    __tablename__ = "parsed_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_requests.id"), nullable=False)

    calories = Column(Integer)
    proteins = Column(Integer)
    fats = Column(Integer)
    carbs = Column(Integer)
    deficiencies = Column(Text)
    recommendations = Column(Text)

    analysis = relationship("AnalysisRequest", back_populates="parsed_result")

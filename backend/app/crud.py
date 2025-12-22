from sqlalchemy.orm import Session
from app import models

def get_or_create_user(db: Session, telegram_id: str) -> models.User:
    user = db.query(models.User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = models.User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def save_analysis(
    db: Session,
    user: models.User,
    input_text: str,
    raw_response: str,
    parsed: dict
):
    analysis = models.AnalysisRequest(
        user_id=user.id,
        input_text=input_text,
        raw_response=raw_response
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    parsed_row = models.ParsedResult(
        analysis_id=analysis.id,
        calories=parsed["calories"],
        proteins=parsed["proteins"],
        fats=parsed["fats"],
        carbs=parsed["carbs"],
        deficiencies=parsed["deficiencies"],
        recommendations=parsed["recommendations"]
    )
    db.add(parsed_row)
    db.commit()

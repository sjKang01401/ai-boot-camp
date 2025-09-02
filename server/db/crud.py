from sqlalchemy.orm import Session
from db import models, schemas

def create_survey(db: Session, survey: schemas.SurveyCreate):
    db_survey = models.Survey(**survey.model_dump())
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey

def get_survey(db: Session, survey_id: int):
    return db.query(models.Survey).filter(models.Survey.id == survey_id).first()

def get_surveys(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Survey).offset(skip).limit(limit).all()

def get_recent_surveys(db: Session, limit: int = 3):
    return db.query(models.Survey).order_by(models.Survey.created_at.desc()).limit(limit).all()

def delete_survey(db: Session, survey_id: int):
    db_survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
    if db_survey:
        db.delete(db_survey)
        db.commit()
    return db_survey
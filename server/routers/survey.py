from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import crud, schemas, database

router = APIRouter(prefix="/api/v1")

@router.post("/surveys/", response_model=schemas.SurveySchema)
def create_survey(survey: schemas.SurveyCreate, db: Session = Depends(database.get_db)):
    return crud.create_survey(db=db, survey=survey)

@router.get("/surveys/recent", response_model=list[schemas.SurveySchema])
def read_recent_surveys(db: Session = Depends(database.get_db)):
    return crud.get_recent_surveys(db)

@router.get("/surveys/{survey_id}", response_model=schemas.SurveySchema)
def read_survey(survey_id: int, db: Session = Depends(database.get_db)):
    db_survey = crud.get_survey(db, survey_id=survey_id)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return db_survey

@router.get("/surveys/", response_model=list[schemas.SurveySchema])
def read_surveys(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    surveys = crud.get_surveys(db, skip=skip, limit=limit)
    return surveys

@router.delete("/surveys/{survey_id}", response_model=schemas.SurveySchema)
def delete_survey(survey_id: int, db: Session = Depends(database.get_db)):
    db_survey = crud.delete_survey(db, survey_id=survey_id)
    if db_survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    return db_survey

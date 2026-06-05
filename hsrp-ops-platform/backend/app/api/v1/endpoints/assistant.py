from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import assistant

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    vehicle_type: str | None = None


@router.post("/ask")
def ask_question(body: AskRequest, db: Session = Depends(get_db)):
    return assistant.ask(db, body.question, body.vehicle_type)


@router.get("/suggestions")
def get_suggestions(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return {"suggestions": assistant.get_suggestions(db, vehicle_type)}

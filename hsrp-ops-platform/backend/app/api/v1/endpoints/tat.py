from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import tat_analysis

router = APIRouter()


@router.get("/by-stage")
def tat_by_stage(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return tat_analysis.get_tat_by_stage(db, vehicle_type)


@router.get("/by-state")
def tat_by_state(db: Session = Depends(get_db)):
    return tat_analysis.get_tat_by_state(db)


@router.get("/by-oem")
def tat_by_oem(db: Session = Depends(get_db)):
    return tat_analysis.get_tat_by_oem(db)


@router.get("/by-eso")
def tat_by_eso(db: Session = Depends(get_db)):
    return tat_analysis.get_tat_by_eso(db)


@router.get("/delay-trends")
def delay_trends(db: Session = Depends(get_db)):
    return tat_analysis.get_delay_trends(db)


@router.get("/recommendations")
def tat_recommendations(db: Session = Depends(get_db)):
    return tat_analysis.get_tat_recommendations(db)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import performance_analytics

router = APIRouter()


@router.get("/active-counts")
def active_counts(db: Session = Depends(get_db)):
    return performance_analytics.get_active_counts(db)


@router.get("/eso")
def eso_performance(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return performance_analytics.get_eso_performance(db, vehicle_type)


@router.get("/rejections/trends")
def rejection_trends(db: Session = Depends(get_db)):
    return performance_analytics.get_rejection_trends(db)


@router.get("/rejections/by-eso")
def rejection_by_eso(db: Session = Depends(get_db)):
    return performance_analytics.get_rejection_by_eso(db)


@router.get("/state-activity")
def state_activity(db: Session = Depends(get_db)):
    return performance_analytics.get_state_activity(db)


@router.get("/oem-trends")
def oem_trends(db: Session = Depends(get_db)):
    return performance_analytics.get_oem_order_trends(db)


@router.get("/dealer-frequency")
def dealer_frequency(db: Session = Depends(get_db)):
    return performance_analytics.get_dealer_frequency(db)


@router.get("/monthly-eso")
def monthly_eso(db: Session = Depends(get_db)):
    return performance_analytics.get_monthly_eso_overview(db)

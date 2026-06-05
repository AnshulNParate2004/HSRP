from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import revenue_analytics

router = APIRouter()


@router.get("/overview")
def revenue_overview(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return revenue_analytics.get_revenue_overview(db, vehicle_type)


@router.get("/by-state")
def revenue_by_state(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return revenue_analytics.get_revenue_by_state(db, vehicle_type)


@router.get("/by-oem")
def revenue_by_oem(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return revenue_analytics.get_revenue_by_oem(db, vehicle_type)


@router.get("/by-portal")
def revenue_by_portal(db: Session = Depends(get_db)):
    return revenue_analytics.get_revenue_by_portal(db)


@router.get("/trends")
def revenue_trends(
    days: int = Query(90, ge=7, le=365),
    granularity: str = Query("week", pattern="^(day|week|month)$"),
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return revenue_analytics.get_revenue_trends(db, days, granularity, vehicle_type)


@router.get("/state-oem-matrix")
def state_oem_matrix(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return revenue_analytics.get_state_oem_matrix(db, vehicle_type)


@router.get("/by-dealer")
def revenue_by_dealer(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return revenue_analytics.get_dealer_contribution(db, vehicle_type)


@router.get("/profitability")
def profitability(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return revenue_analytics.get_profitability_by_state(db, vehicle_type)


@router.get("/oem-comparison")
def oem_comparison(db: Session = Depends(get_db)):
    return revenue_analytics.get_oem_comparison(db)

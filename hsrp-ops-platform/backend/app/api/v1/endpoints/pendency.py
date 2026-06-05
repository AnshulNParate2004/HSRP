from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import pendency_monitor

router = APIRouter()


@router.get("/overview")
def pendency_overview(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return pendency_monitor.get_pendency_overview(db, vehicle_type)


@router.get("/by-stage")
def pendency_by_stage(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return pendency_monitor.get_pendency_by_stage(db, vehicle_type)


@router.get("/by-state")
def pendency_by_state(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return pendency_monitor.get_pendency_by_state(db, vehicle_type)


@router.get("/by-eso")
def pendency_by_eso(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return pendency_monitor.get_pendency_by_eso(db, vehicle_type)


@router.get("/critical")
def critical_pendencies(db: Session = Depends(get_db)):
    return pendency_monitor.get_critical_pendencies(db)


@router.get("/by-oem")
def pendency_by_oem(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return pendency_monitor.get_pendency_by_oem(db, vehicle_type)


@router.get("/monthly-overview")
def monthly_overview(db: Session = Depends(get_db)):
    return pendency_monitor.get_monthly_stage_overview(db)


@router.get("/eso-delay-by-date")
def eso_delay_by_date(db: Session = Depends(get_db)):
    return pendency_monitor.get_eso_delay_by_date(db)

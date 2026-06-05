from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import platform_config

router = APIRouter()


@router.get("/ui")
def get_ui_config(db: Session = Depends(get_db)):
    return platform_config.get_ui_config(db)


@router.get("/dashboard-metrics")
def dashboard_metrics(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return {"metrics": platform_config.get_dashboard_metrics(db, vehicle_type)}


@router.get("/monitoring-metrics")
def monitoring_metrics(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return {"metrics": platform_config.get_monitoring_metrics(db, vehicle_type)}


@router.get("/stages")
def order_stages(db: Session = Depends(get_db)):
    cfg = platform_config.get_ui_config(db)
    return {"stages": cfg["order_stages"]}

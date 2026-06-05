from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import dashboard as dashboard_service
from app.services import platform_config

router = APIRouter()


@router.get("/summary")
def get_summary(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    summary = dashboard_service.get_dashboard_summary(db, vehicle_type)
    return {
        **summary,
        "metrics": platform_config.get_dashboard_metrics(db, vehicle_type),
    }

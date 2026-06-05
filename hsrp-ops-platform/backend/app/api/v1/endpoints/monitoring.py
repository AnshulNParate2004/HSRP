from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import monitoring

router = APIRouter()


@router.get("/live")
def live_summary(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return monitoring.get_live_summary(db, vehicle_type)


@router.get("/states")
def state_tracking(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return monitoring.get_state_live_tracking(db, vehicle_type)


@router.get("/eso-workload")
def eso_workload(db: Session = Depends(get_db)):
    return monitoring.get_eso_workload(db)


@router.get("/embossing")
def embossing(db: Session = Depends(get_db)):
    return monitoring.get_embossing_monitoring(db)


@router.get("/dispatch")
def dispatch(db: Session = Depends(get_db)):
    return monitoring.get_dispatch_monitoring(db)


@router.get("/dealers")
def dealers(db: Session = Depends(get_db)):
    return monitoring.get_dealer_activity(db)

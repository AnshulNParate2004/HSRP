from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import AlertOut
from app.services import ai_alerts

router = APIRouter()


@router.get("", response_model=list[AlertOut])
def list_alerts(
    severity: str | None = Query(None, pattern="^(low|medium|high|critical)$"),
    unresolved_only: bool = True,
    db: Session = Depends(get_db),
):
    return ai_alerts.get_alerts(db, severity, unresolved_only)


@router.post("/generate", response_model=list[AlertOut])
def generate_alerts(
    clear_existing: bool = True,
    db: Session = Depends(get_db),
):
    """Re-run alert rules. Clears unresolved alerts by default to avoid duplicates."""
    return ai_alerts.generate_alerts(db, clear_existing)

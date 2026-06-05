from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, require_min_role, require_roles
from app.db.session import get_db
from app.models.entities import PortalSyncLog
from app.services.integrations.sync import (
    get_portal_status,
    purge_skipped_sync_logs,
    sync_all_portals,
)

router = APIRouter()


@router.get("/status")
def integration_status(user: CurrentUser):
    return {"portals": get_portal_status()}


@router.post("/sync")
def trigger_portal_sync(
    user: CurrentUser,
    db: Session = Depends(get_db),
    _: None = Depends(require_min_role("operations_manager")),
):
    return {"results": sync_all_portals(db, source="manual")}


@router.get("/sync/logs")
def portal_sync_logs(
    user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int = Query(30, le=100),
):
    logs = (
        db.query(PortalSyncLog)
        .filter(PortalSyncLog.status != "skipped")
        .order_by(PortalSyncLog.started_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": log.id,
            "portal_name": log.portal_name,
            "status": log.status,
            "records_fetched": log.records_fetched,
            "records_upserted": log.records_upserted,
            "error_message": log.error_message,
            "started_at": log.started_at.isoformat(),
            "finished_at": log.finished_at.isoformat() if log.finished_at else None,
        }
        for log in logs
    ]


@router.delete("/sync/logs/skipped", dependencies=[Depends(require_roles("admin"))])
def clear_skipped_logs(db: Session = Depends(get_db)):
    count = purge_skipped_sync_logs(db)
    return {"deleted": count, "message": f"Removed {count} skipped sync log entries"}

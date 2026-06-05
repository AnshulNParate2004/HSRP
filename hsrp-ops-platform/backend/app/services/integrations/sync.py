"""Upsert orders from configured OEM portals."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Dealer, ESO, OEM, Order, Portal, PortalSyncLog, State
from app.services.integrations.base import PortalAdapter, PortalOrderPayload
from app.services.integrations.http_portal import HttpJsonPortalAdapter


def get_portal_adapters() -> list[PortalAdapter]:
    return [
        HttpJsonPortalAdapter("DISHA", settings.DISHA_API_URL, settings.DISHA_API_KEY),
        HttpJsonPortalAdapter("Hero Biz", settings.HERO_BIZ_API_URL, settings.HERO_BIZ_API_KEY),
        HttpJsonPortalAdapter(
            "Old Vehicle Portal",
            settings.OLD_VEHICLE_PORTAL_API_URL,
            settings.OLD_VEHICLE_PORTAL_API_KEY,
        ),
        HttpJsonPortalAdapter("POS", settings.POS_PORTAL_API_URL, settings.POS_PORTAL_API_KEY),
    ]


def any_portal_configured() -> bool:
    return any(a.is_configured() for a in get_portal_adapters())


def get_portal_status() -> list[dict]:
    return [
        {
            "portal_name": a.portal_name,
            "configured": a.is_configured(),
            "message": "Ready to sync" if a.is_configured() else "Set API URL and key in backend .env",
        }
        for a in get_portal_adapters()
    ]


def sync_all_portals(db: Session, *, source: str = "manual") -> list[dict]:
    """Sync all portals. Only writes DB logs for real sync attempts (not unconfigured skips)."""
    since = datetime.utcnow() - timedelta(hours=24)
    results = []
    for adapter in get_portal_adapters():
        results.append(_sync_adapter(db, adapter, since, source=source))
    return results


def _sync_adapter(db: Session, adapter: PortalAdapter, since: datetime, *, source: str) -> dict:
    if not adapter.is_configured():
        return {
            "portal": adapter.portal_name,
            "status": "skipped",
            "reason": "not_configured",
            "fetched": 0,
            "upserted": 0,
            "message": "Add DISHA_API_URL and DISHA_API_KEY (etc.) in backend .env",
        }

    started = datetime.utcnow()
    log = PortalSyncLog(portal_name=adapter.portal_name, status="running", started_at=started)

    try:
        rows = adapter.fetch_orders(since=since)
        upserted = 0
        for payload in rows:
            if _upsert_order(db, payload):
                upserted += 1
        db.flush()
        log.status = "success"
        log.records_fetched = len(rows)
        log.records_upserted = upserted
    except Exception as exc:
        log.status = "failed"
        log.error_message = str(exc)[:2000]

    log.finished_at = datetime.utcnow()
    db.add(log)
    db.commit()

    return {
        "portal": adapter.portal_name,
        "status": log.status,
        "fetched": log.records_fetched,
        "upserted": log.records_upserted,
        "error": log.error_message,
    }


def purge_skipped_sync_logs(db: Session) -> int:
    deleted = (
        db.query(PortalSyncLog)
        .filter(PortalSyncLog.status == "skipped")
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted


def _upsert_order(db: Session, payload: PortalOrderPayload) -> bool:
    portal = db.query(Portal).filter(Portal.name == payload.portal_name).first()
    if not portal:
        return False
    state = db.query(State).filter(State.code == payload.state_code.upper()).first()
    if not state:
        state = db.query(State).filter(State.name.ilike(f"%{payload.state_code}%")).first()
    if not state:
        return False
    oem = db.query(OEM).filter(OEM.name.ilike(payload.oem_name)).first()
    if not oem:
        oem = OEM(name=payload.oem_name, is_active=True)
        db.add(oem)
        db.flush()

    existing = db.query(Order).filter(
        Order.external_id == payload.external_id,
        Order.portal_id == portal.id,
    ).first()

    now = datetime.utcnow()
    if existing:
        existing.current_stage = payload.current_stage
        existing.revenue = payload.revenue
        existing.last_synced_at = now
        return False

    eso = db.query(ESO).filter(ESO.state_id == state.id, ESO.is_active.is_(True)).first()
    dealer = None
    if payload.dealer_name:
        dealer = db.query(Dealer).filter(Dealer.name == payload.dealer_name, Dealer.state_id == state.id).first()

    order = Order(
        order_number=payload.order_number,
        external_id=payload.external_id,
        vehicle_type=payload.vehicle_type if payload.vehicle_type in ("new", "old") else "new",
        oem_id=oem.id,
        state_id=state.id,
        eso_id=eso.id if eso else None,
        dealer_id=dealer.id if dealer else None,
        portal_id=portal.id,
        revenue=payload.revenue,
        current_stage=payload.current_stage,
        order_date=payload.order_date,
        stage_entered_at=payload.order_date,
        last_synced_at=now,
    )
    db.add(order)
    return True

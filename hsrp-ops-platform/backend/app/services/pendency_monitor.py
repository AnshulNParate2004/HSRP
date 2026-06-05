"""Pendency & delay monitoring — stage bottlenecks and SLA breaches."""

from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import ESO, Order, State

STAGE_SLA_HOURS = {
    "issuance_pending": settings.SLA_ISSUANCE_HOURS,
    "embossing_pending": settings.SLA_EMBOSSING_HOURS,
    "dc_pending": settings.SLA_DC_HOURS,
    "dispatch_pending": settings.SLA_DISPATCH_HOURS,
    "fitment_pending": settings.SLA_FITMENT_HOURS,
}

PENDING_STAGES = list(STAGE_SLA_HOURS.keys())


def _hours_in_stage(order: Order) -> float:
    delta = datetime.utcnow() - order.stage_entered_at
    return round(delta.total_seconds() / 3600, 1)


def get_pendency_overview(db: Session, vehicle_type: str | None = None) -> dict:
    q = db.query(Order).filter(Order.current_stage.in_(PENDING_STAGES + ["received"]))
    if vehicle_type:
        q = q.filter(Order.vehicle_type == vehicle_type)
    pending = q.all()
    delayed = [o for o in pending if o.current_stage in STAGE_SLA_HOURS and _hours_in_stage(o) > STAGE_SLA_HOURS[o.current_stage]]
    return {
        "total_pending": len(pending),
        "total_delayed": len(delayed),
        "delay_rate_pct": round(len(delayed) / max(len(pending), 1) * 100, 1),
        "vehicle_type": vehicle_type or "all",
    }


def get_pendency_by_stage(db: Session, vehicle_type: str | None = None) -> list[dict]:
    results = []
    for stage in PENDING_STAGES:
        q = db.query(Order).filter(Order.current_stage == stage)
        if vehicle_type:
            q = q.filter(Order.vehicle_type == vehicle_type)
        orders = q.all()
        sla = STAGE_SLA_HOURS[stage]
        delayed = [o for o in orders if _hours_in_stage(o) > sla]
        avg_hours = round(sum(_hours_in_stage(o) for o in orders) / max(len(orders), 1), 1)
        results.append({
            "stage": stage,
            "pending_count": len(orders),
            "delayed_count": len(delayed),
            "sla_hours": sla,
            "avg_hours_in_stage": avg_hours,
        })
    return results


def get_pendency_by_state(db: Session, vehicle_type: str | None = None) -> list[dict]:
    q = (
        db.query(
            State.id,
            State.name,
            func.count(Order.id).label("pending_count"),
        )
        .join(Order, Order.state_id == State.id)
        .filter(Order.current_stage.in_(PENDING_STAGES))
    )
    if vehicle_type:
        q = q.filter(Order.vehicle_type == vehicle_type)
    rows = q.group_by(State.id, State.name).order_by(func.count(Order.id).desc()).all()
    return [{"id": r.id, "name": r.name, "pending_count": r.pending_count} for r in rows]


def get_pendency_by_eso(db: Session, vehicle_type: str | None = None) -> list[dict]:
    q = (
        db.query(
            ESO.id,
            ESO.name,
            State.name.label("state_name"),
            func.count(Order.id).label("pending_count"),
        )
        .join(Order, Order.eso_id == ESO.id)
        .join(State, ESO.state_id == State.id)
        .filter(Order.current_stage.in_(PENDING_STAGES))
    )
    if vehicle_type:
        q = q.filter(Order.vehicle_type == vehicle_type)
    rows = q.group_by(ESO.id, ESO.name, State.name).order_by(func.count(Order.id).desc()).limit(20).all()
    return [
        {"id": r.id, "name": r.name, "state_name": r.state_name, "pending_count": r.pending_count}
        for r in rows
    ]


def get_critical_pendencies(db: Session, limit: int = 25) -> list[dict]:
    """Orders exceeding SLA — for escalation."""
    critical = []
    for stage, sla in STAGE_SLA_HOURS.items():
        orders = db.query(Order).filter(Order.current_stage == stage).all()
        for o in orders:
            hours = _hours_in_stage(o)
            if hours > sla:
                critical.append({
                    "order_id": o.id,
                    "order_number": o.order_number,
                    "stage": stage,
                    "hours_in_stage": hours,
                    "sla_hours": sla,
                    "overdue_hours": round(hours - sla, 1),
                    "vehicle_type": o.vehicle_type,
                    "state_id": o.state_id,
                    "eso_id": o.eso_id,
                })
    critical.sort(key=lambda x: x["overdue_hours"], reverse=True)
    return critical[:limit]


def get_pendency_by_oem(db: Session, vehicle_type: str | None = None) -> list[dict]:
    from app.models.entities import OEM

    q = (
        db.query(
            OEM.name,
            func.count(Order.id).label("pending_count"),
        )
        .join(Order, Order.oem_id == OEM.id)
        .filter(Order.current_stage.in_(PENDING_STAGES))
    )
    if vehicle_type:
        q = q.filter(Order.vehicle_type == vehicle_type)
    rows = q.group_by(OEM.name).order_by(func.count(Order.id).desc()).all()
    return [{"oem_name": r.name, "pending_count": r.pending_count} for r in rows]


def get_monthly_stage_overview(db: Session) -> list[dict]:
    since = datetime.utcnow() - timedelta(days=180)
    orders = db.query(Order).filter(Order.order_date >= since).all()
    buckets: dict[str, dict[str, int]] = {}
    for o in orders:
        month = o.order_date.strftime("%Y-%m")
        if month not in buckets:
            buckets[month] = {}
        stage = o.current_stage
        buckets[month][stage] = buckets[month].get(stage, 0) + 1
    return [
        {"month": m, **stages}
        for m, stages in sorted(buckets.items())
    ]


def get_eso_delay_by_date(db: Session, days: int = 30) -> list[dict]:
    since = datetime.utcnow() - timedelta(days=days)
    orders = (
        db.query(Order)
        .filter(
            Order.current_stage.in_(PENDING_STAGES),
            Order.stage_entered_at >= since,
        )
        .all()
    )
    buckets: dict[str, int] = {}
    for o in orders:
        hours = _hours_in_stage(o)
        if hours > STAGE_SLA_HOURS.get(o.current_stage, 24):
            key = o.stage_entered_at.strftime("%Y-%m-%d")
            buckets[key] = buckets.get(key, 0) + 1
    return [{"date": d, "delayed_count": c} for d, c in sorted(buckets.items())]

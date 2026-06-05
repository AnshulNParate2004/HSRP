"""TAT (Turnaround Time) analysis across order lifecycle stages."""

from sqlalchemy.orm import Session

from app.models.entities import Order, OrderStageHistory


STAGE_ORDER = [
    "received",
    "issuance_pending",
    "embossing_pending",
    "dc_pending",
    "dispatch_pending",
    "fitment_pending",
    "completed",
]

STAGE_LABELS = {
    "received": "Order Received",
    "issuance_pending": "Order → Issuance",
    "embossing_pending": "Issuance → Embossing",
    "dc_pending": "Embossing → DC",
    "dispatch_pending": "DC → Dispatch",
    "fitment_pending": "Dispatch → Fitment",
    "completed": "Fitment → Complete",
}


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    idx = int(len(sorted_vals) * pct / 100)
    idx = min(idx, len(sorted_vals) - 1)
    return round(sorted_vals[idx], 1)


def get_tat_by_stage(db: Session, vehicle_type: str | None = None) -> list[dict]:
    results = []
    for stage in STAGE_ORDER:
        q = db.query(OrderStageHistory).filter(
            OrderStageHistory.stage == stage,
            OrderStageHistory.tat_hours.isnot(None),
        )
        if vehicle_type:
            q = q.join(Order).filter(Order.vehicle_type == vehicle_type)
        rows = q.all()
        values = [r.tat_hours for r in rows if r.tat_hours is not None]
        results.append({
            "stage": stage,
            "label": STAGE_LABELS.get(stage, stage),
            "avg_hours": round(sum(values) / max(len(values), 1), 1),
            "p90_hours": _percentile(values, 90),
            "sample_count": len(values),
        })
    return results


def get_tat_by_state(db: Session) -> list[dict]:
    from sqlalchemy.orm import joinedload
    from app.models.entities import State

    states = db.query(State).all()
    results = []
    for state in states:
        orders = db.query(Order).filter(Order.state_id == state.id, Order.current_stage == "completed").all()
        total_tat = 0.0
        count = 0
        for o in orders:
            history = db.query(OrderStageHistory).filter(OrderStageHistory.order_id == o.id).all()
            order_tat = sum(h.tat_hours or 0 for h in history)
            if order_tat > 0:
                total_tat += order_tat
                count += 1
        results.append({
            "state_name": state.name,
            "avg_total_tat_hours": round(total_tat / max(count, 1), 1),
            "completed_orders": count,
        })
    results.sort(key=lambda x: x["avg_total_tat_hours"])
    return results


def get_tat_by_oem(db: Session) -> list[dict]:
    from app.models.entities import OEM

    oems = db.query(OEM).filter(OEM.is_active.is_(True)).all()
    results = []
    for oem in oems:
        orders = db.query(Order).filter(Order.oem_id == oem.id, Order.current_stage == "completed").all()
        total_tat = 0.0
        count = 0
        for o in orders:
            history = db.query(OrderStageHistory).filter(OrderStageHistory.order_id == o.id).all()
            order_tat = sum(h.tat_hours or 0 for h in history)
            if order_tat > 0:
                total_tat += order_tat
                count += 1
        results.append({
            "oem_name": oem.name,
            "avg_total_tat_hours": round(total_tat / max(count, 1), 1),
            "completed_orders": count,
        })
    return results


def get_overall_avg_tat(db: Session, vehicle_type: str | None = None) -> float:
    q = (
        db.query(OrderStageHistory)
        .join(Order, OrderStageHistory.order_id == Order.id)
        .filter(OrderStageHistory.tat_hours.isnot(None))
    )
    if vehicle_type in ("new", "old"):
        q = q.filter(Order.vehicle_type == vehicle_type)
    rows = q.all()
    values = [r.tat_hours for r in rows if r.tat_hours]
    return round(sum(values) / max(len(values), 1), 1)


def get_tat_by_eso(db: Session) -> list[dict]:
    from app.models.entities import ESO

    esos = db.query(ESO).filter(ESO.is_active.is_(True)).all()
    results = []
    for eso in esos:
        orders = db.query(Order).filter(Order.eso_id == eso.id, Order.current_stage == "completed").all()
        total_tat = 0.0
        count = 0
        for o in orders:
            history = db.query(OrderStageHistory).filter(OrderStageHistory.order_id == o.id).all()
            order_tat = sum(h.tat_hours or 0 for h in history)
            if order_tat > 0:
                total_tat += order_tat
                count += 1
        if count > 0:
            results.append({
                "eso_name": eso.name,
                "avg_total_tat_hours": round(total_tat / count, 1),
                "completed_orders": count,
            })
    results.sort(key=lambda x: x["avg_total_tat_hours"], reverse=True)
    return results


def get_delay_trends(db: Session, weeks: int = 8) -> list[dict]:
    from datetime import datetime, timedelta
    from app.services.pendency_monitor import get_eso_delay_by_date

    return get_eso_delay_by_date(db, days=weeks * 7)


def get_tat_recommendations(db: Session) -> list[dict]:
    stages = get_tat_by_stage(db)
    recs = []
    for s in stages:
        if s["sample_count"] > 0 and s["avg_hours"] > 48:
            recs.append({
                "stage": s["label"],
                "avg_hours": s["avg_hours"],
                "recommendation": f"Optimize {s['label']} — avg {s['avg_hours']}h exceeds 48h benchmark. Review ESO capacity and material flow.",
            })
    states = get_tat_by_state(db)
    if states:
        slow = max(states, key=lambda x: x["avg_total_tat_hours"])
        if slow["completed_orders"] > 0:
            recs.append({
                "stage": "State benchmark",
                "avg_hours": slow["avg_total_tat_hours"],
                "recommendation": f"{slow['state_name']} has highest total TAT ({slow['avg_total_tat_hours']}h). Prioritize state ops review.",
            })
    return recs

"""Operational performance — ESO productivity, rejections, active counts."""

from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.entities import Dealer, ESO, OEM, Order, OrderStageHistory, Rejection, State


def get_active_counts(db: Session) -> dict:
    return {
        "active_oems": db.query(OEM).filter(OEM.is_active.is_(True)).count(),
        "active_esos": db.query(ESO).filter(ESO.is_active.is_(True)).count(),
        "active_dealers": db.query(Dealer).filter(Dealer.is_active.is_(True)).count(),
        "states_with_orders": db.query(func.count(func.distinct(Order.state_id))).scalar(),
    }


def get_eso_performance(db: Session, vehicle_type: str | None = None) -> list[dict]:
    esos = db.query(ESO).options(joinedload(ESO.state)).filter(ESO.is_active.is_(True)).all()
    results = []
    for eso in esos:
        q = db.query(Order).filter(Order.eso_id == eso.id)
        if vehicle_type:
            q = q.filter(Order.vehicle_type == vehicle_type)
        orders = q.all()
        completed = [o for o in orders if o.current_stage == "completed"]
        rejections = db.query(Rejection).filter(Rejection.eso_id == eso.id).count()

        tat_values = []
        for o in completed:
            history = (
                db.query(OrderStageHistory)
                .filter(OrderStageHistory.order_id == o.id, OrderStageHistory.tat_hours.isnot(None))
                .all()
            )
            tat_values.extend(h.tat_hours for h in history if h.tat_hours)

        avg_tat = round(sum(tat_values) / max(len(tat_values), 1), 1) if tat_values else 0.0
        completion_rate = round(len(completed) / max(len(orders), 1) * 100, 1)

        results.append({
            "eso_id": eso.id,
            "eso_name": eso.name,
            "state_name": eso.state.name if eso.state else "",
            "total_orders": len(orders),
            "completed_orders": len(completed),
            "completion_rate": completion_rate,
            "rejection_count": rejections,
            "avg_tat_hours": avg_tat,
        })
    results.sort(key=lambda x: x["completion_rate"])
    return results


def get_rejection_trends(db: Session, weeks: int = 8) -> list[dict]:
    since = datetime.utcnow() - timedelta(weeks=weeks)
    rejections = (
        db.query(Rejection)
        .filter(Rejection.rejected_at >= since)
        .order_by(Rejection.rejected_at)
        .all()
    )
    buckets: dict[str, int] = {}
    for r in rejections:
        key = r.rejected_at.strftime("%Y-W%W")
        buckets[key] = buckets.get(key, 0) + 1
    return [{"period": k, "rejection_count": v} for k, v in sorted(buckets.items())]


def get_rejection_by_eso(db: Session, limit: int = 15) -> list[dict]:
    rows = (
        db.query(
            ESO.id,
            ESO.name,
            State.name.label("state_name"),
            func.count(Rejection.id).label("rejection_count"),
        )
        .join(Rejection, Rejection.eso_id == ESO.id)
        .join(State, ESO.state_id == State.id)
        .group_by(ESO.id, ESO.name, State.name)
        .order_by(func.count(Rejection.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {"eso_id": r.id, "eso_name": r.name, "state_name": r.state_name, "rejection_count": r.rejection_count}
        for r in rows
    ]


def get_state_activity(db: Session) -> list[dict]:
    rows = (
        db.query(State.name, func.count(Order.id).label("order_count"))
        .join(Order, Order.state_id == State.id)
        .group_by(State.name)
        .order_by(func.count(Order.id).desc())
        .all()
    )
    results = []
    for r in rows:
        completed = (
            db.query(Order)
            .join(State, Order.state_id == State.id)
            .filter(State.name == r.name, Order.current_stage == "completed")
            .count()
        )
        results.append({
            "state_name": r.name,
            "order_count": r.order_count,
            "completed_count": completed,
        })
    return results


def get_oem_order_trends(db: Session, weeks: int = 12) -> list[dict]:
    from datetime import datetime, timedelta
    from app.models.entities import OEM

    since = datetime.utcnow() - timedelta(weeks=weeks)
    orders = db.query(Order).filter(Order.order_date >= since).all()
    oem_names = {o.id: o.name for o in db.query(OEM).all()}
    buckets: dict[str, dict[str, int]] = {}
    for o in orders:
        period = o.order_date.strftime("%Y-W%W")
        oem = oem_names.get(o.oem_id, "Unknown")
        if period not in buckets:
            buckets[period] = {}
        buckets[period][oem] = buckets[period].get(oem, 0) + 1
    top_oems = sorted(
        {oem for counts in buckets.values() for oem in counts},
        key=lambda n: sum(counts.get(n, 0) for counts in buckets.values()),
        reverse=True,
    )[:5]
    return [
        {"period": p, **{oem: counts.get(oem, 0) for oem in top_oems}}
        for p, counts in sorted(buckets.items())
    ]


def get_dealer_frequency(db: Session, limit: int = 15) -> list[dict]:
    from app.models.entities import Dealer

    rows = (
        db.query(
            Dealer.name,
            Dealer.dealer_type,
            State.name.label("state_name"),
            func.count(Order.id).label("order_count"),
        )
        .join(Order, Order.dealer_id == Dealer.id)
        .join(State, Dealer.state_id == State.id)
        .group_by(Dealer.name, Dealer.dealer_type, State.name)
        .order_by(func.count(Order.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "dealer_name": r.name,
            "dealer_type": r.dealer_type,
            "state_name": r.state_name,
            "order_count": r.order_count,
        }
        for r in rows
    ]


def get_monthly_eso_overview(db: Session) -> list[dict]:
    from datetime import datetime, timedelta

    since = datetime.utcnow() - timedelta(days=90)
    esos = db.query(ESO).filter(ESO.is_active.is_(True)).all()
    results = []
    for eso in esos:
        recent = db.query(Order).filter(Order.eso_id == eso.id, Order.order_date >= since).count()
        completed = db.query(Order).filter(
            Order.eso_id == eso.id, Order.current_stage == "completed", Order.order_date >= since
        ).count()
        results.append({
            "eso_name": eso.name,
            "orders_90d": recent,
            "completed_90d": completed,
            "completion_rate": round(completed / max(recent, 1) * 100, 1),
        })
    results.sort(key=lambda x: x["completion_rate"])
    return results

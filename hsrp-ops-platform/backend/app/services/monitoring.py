"""Real-time operational monitoring — ESO workload, embossing, dispatch, dealers."""

from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import Dealer, ESO, Order, State
from app.services.vehicle_filter import filter_orders


def get_live_summary(db: Session, vehicle_type: str | None = None) -> dict:
    now = datetime.utcnow()
    last_hour = now - timedelta(hours=1)
    active_base = db.query(Order).filter(Order.current_stage != "completed")
    if vehicle_type == "new":
        new_live = filter_orders(active_base, "new").count()
        old_live = 0
        total_active = new_live
    elif vehicle_type == "old":
        old_live = filter_orders(active_base, "old").count()
        new_live = 0
        total_active = old_live
    else:
        total_active = active_base.count()
        new_live = db.query(Order).filter(
            Order.vehicle_type == "new", Order.current_stage != "completed"
        ).count()
        old_live = db.query(Order).filter(
            Order.vehicle_type == "old", Order.current_stage != "completed"
        ).count()

    hour_q = db.query(Order).filter(Order.order_date >= last_hour)
    emboss_q = db.query(Order).filter(Order.current_stage == "embossing_pending")
    dispatch_q = db.query(Order).filter(Order.current_stage == "dispatch_pending")
    fitment_q = db.query(Order).filter(Order.current_stage == "fitment_pending")

    return {
        "total_active_orders": total_active,
        "new_vehicle_live": new_live,
        "old_vehicle_live": old_live,
        "orders_last_hour": filter_orders(hour_q, vehicle_type).count(),
        "in_embossing": filter_orders(emboss_q, vehicle_type).count(),
        "in_dispatch": filter_orders(dispatch_q, vehicle_type).count(),
        "in_fitment": filter_orders(fitment_q, vehicle_type).count(),
        "timestamp": now.isoformat(),
        "vehicle_type": vehicle_type or "all",
    }


def get_state_live_tracking(db: Session, vehicle_type: str | None = None) -> list[dict]:
    states = db.query(State).all()
    results = []
    for state in states:
        active_q = db.query(Order).filter(
            Order.state_id == state.id, Order.current_stage != "completed"
        )
        active = filter_orders(active_q, vehicle_type).all()
        if not active:
            continue
        new_count = sum(1 for o in active if o.vehicle_type == "new")
        old_count = sum(1 for o in active if o.vehicle_type == "old")
        results.append({
            "state_name": state.name,
            "active_orders": len(active),
            "new_vehicle": new_count,
            "old_vehicle": old_count,
        })
    results.sort(key=lambda x: x["active_orders"], reverse=True)
    return results


def get_eso_workload(db: Session) -> list[dict]:
    from app.services.forecasting import predict_workload
    return predict_workload(db)


def get_embossing_monitoring(db: Session) -> dict:
    orders = db.query(Order).filter(Order.current_stage == "embossing_pending").all()
    delayed = sum(
        1 for o in orders
        if (datetime.utcnow() - o.stage_entered_at).total_seconds() / 3600 > 48
    )
    return {
        "station_count": db.query(ESO).filter(ESO.is_active.is_(True)).count(),
        "orders_in_embossing": len(orders),
        "delayed_count": delayed,
        "avg_wait_hours": round(
            sum((datetime.utcnow() - o.stage_entered_at).total_seconds() / 3600 for o in orders)
            / max(len(orders), 1),
            1,
        ),
    }


def get_dispatch_monitoring(db: Session) -> dict:
    orders = db.query(Order).filter(Order.current_stage == "dispatch_pending").all()
    delayed = sum(
        1 for o in orders
        if (datetime.utcnow() - o.stage_entered_at).total_seconds() / 3600 > 48
    )
    return {
        "orders_in_dispatch": len(orders),
        "delayed_dispatch": delayed,
        "states_affected": len({o.state_id for o in orders}),
    }


def get_dealer_activity(db: Session, limit: int = 20) -> list[dict]:
    rows = (
        db.query(
            Dealer.id,
            Dealer.name,
            Dealer.dealer_type,
            State.name.label("state_name"),
            func.count(Order.id).label("order_count"),
            func.coalesce(func.sum(Order.revenue), 0.0).label("revenue"),
        )
        .outerjoin(Order, Order.dealer_id == Dealer.id)
        .join(State, Dealer.state_id == State.id)
        .filter(Dealer.is_active.is_(True))
        .group_by(Dealer.id, Dealer.name, Dealer.dealer_type, State.name)
        .order_by(func.count(Order.id).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "dealer_id": r.id,
            "dealer_name": r.name,
            "dealer_type": r.dealer_type,
            "state_name": r.state_name,
            "order_count": r.order_count,
            "revenue": round(float(r.revenue), 2),
        }
        for r in rows
    ]

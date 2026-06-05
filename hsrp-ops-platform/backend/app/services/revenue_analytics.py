"""Revenue analytics — state/OEM/portal contribution and trends."""

from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import Order, OEM, Portal, State


def _base_order_query(db: Session, vehicle_type: str | None = None):
    q = db.query(Order)
    if vehicle_type:
        q = q.filter(Order.vehicle_type == vehicle_type)
    return q


def get_revenue_overview(db: Session, vehicle_type: str | None = None) -> dict:
    q = _base_order_query(db, vehicle_type)
    total_orders = q.count()
    total_revenue = db.query(func.coalesce(func.sum(Order.revenue), 0.0)).scalar() or 0.0
    if vehicle_type:
        total_revenue = (
            db.query(func.coalesce(func.sum(Order.revenue), 0.0))
            .filter(Order.vehicle_type == vehicle_type)
            .scalar()
            or 0.0
        )
    return {
        "total_orders": total_orders if not vehicle_type else q.count(),
        "total_revenue": round(float(total_revenue), 2),
        "vehicle_type": vehicle_type or "all",
    }


def get_revenue_by_state(db: Session, vehicle_type: str | None = None, limit: int = 20) -> list[dict]:
    q = (
        db.query(
            State.id,
            State.name,
            func.count(Order.id).label("order_count"),
            func.coalesce(func.sum(Order.revenue), 0.0).label("revenue"),
        )
        .join(Order, Order.state_id == State.id)
    )
    if vehicle_type:
        q = q.filter(Order.vehicle_type == vehicle_type)
    rows = q.group_by(State.id, State.name).order_by(func.sum(Order.revenue).desc()).limit(limit).all()
    total_rev = sum(r.revenue for r in rows) or 1
    return [
        {
            "id": r.id,
            "name": r.name,
            "order_count": r.order_count,
            "revenue": round(float(r.revenue), 2),
            "percentage": round(float(r.revenue) / total_rev * 100, 1),
        }
        for r in rows
    ]


def get_revenue_by_oem(db: Session, vehicle_type: str | None = None, limit: int = 15) -> list[dict]:
    q = (
        db.query(
            OEM.id,
            OEM.name,
            func.count(Order.id).label("order_count"),
            func.coalesce(func.sum(Order.revenue), 0.0).label("revenue"),
        )
        .join(Order, Order.oem_id == OEM.id)
    )
    if vehicle_type:
        q = q.filter(Order.vehicle_type == vehicle_type)
    rows = q.group_by(OEM.id, OEM.name).order_by(func.sum(Order.revenue).desc()).limit(limit).all()
    total_rev = sum(r.revenue for r in rows) or 1
    return [
        {
            "id": r.id,
            "name": r.name,
            "order_count": r.order_count,
            "revenue": round(float(r.revenue), 2),
            "percentage": round(float(r.revenue) / total_rev * 100, 1),
        }
        for r in rows
    ]


def get_revenue_by_portal(db: Session) -> list[dict]:
    rows = (
        db.query(
            Portal.id,
            Portal.name,
            func.count(Order.id).label("order_count"),
            func.coalesce(func.sum(Order.revenue), 0.0).label("revenue"),
        )
        .join(Order, Order.portal_id == Portal.id)
        .group_by(Portal.id, Portal.name)
        .order_by(func.sum(Order.revenue).desc())
        .all()
    )
    total_rev = sum(r.revenue for r in rows) or 1
    return [
        {
            "id": r.id,
            "name": r.name,
            "order_count": r.order_count,
            "revenue": round(float(r.revenue), 2),
            "percentage": round(float(r.revenue) / total_rev * 100, 1),
        }
        for r in rows
    ]


def get_revenue_trends(
    db: Session,
    days: int = 90,
    granularity: str = "week",
    vehicle_type: str | None = None,
) -> list[dict]:
    """Daily or weekly order/revenue trend for charting."""
    since = datetime.utcnow() - timedelta(days=days)
    q = db.query(Order).filter(Order.order_date >= since)
    if vehicle_type in ("new", "old"):
        q = q.filter(Order.vehicle_type == vehicle_type)
    orders = q.order_by(Order.order_date).all()
    buckets: dict[str, dict] = {}
    for o in orders:
        if granularity == "day":
            key = o.order_date.strftime("%Y-%m-%d")
        elif granularity == "month":
            key = o.order_date.strftime("%Y-%m")
        else:
            key = o.order_date.strftime("%Y-W%W")
        if key not in buckets:
            buckets[key] = {"period": key, "order_count": 0, "revenue": 0.0}
        buckets[key]["order_count"] += 1
        buckets[key]["revenue"] += o.revenue
    return [
        {**v, "revenue": round(v["revenue"], 2)}
        for v in sorted(buckets.values(), key=lambda x: x["period"])
    ]


def get_state_oem_matrix(db: Session, vehicle_type: str | None = None) -> list[dict]:
    """State × OEM cross-tab for heatmap."""
    q = (
        db.query(
            State.name.label("state"),
            OEM.name.label("oem"),
            func.count(Order.id).label("order_count"),
            func.coalesce(func.sum(Order.revenue), 0.0).label("revenue"),
        )
        .join(State, Order.state_id == State.id)
        .join(OEM, Order.oem_id == OEM.id)
    )
    if vehicle_type:
        q = q.filter(Order.vehicle_type == vehicle_type)
    rows = q.group_by(State.name, OEM.name).all()
    return [
        {
            "state": r.state,
            "oem": r.oem,
            "order_count": r.order_count,
            "revenue": round(float(r.revenue), 2),
        }
        for r in rows
    ]


def get_dealer_contribution(db: Session, vehicle_type: str | None = None, limit: int = 20) -> list[dict]:
    from app.models.entities import Dealer

    q = (
        db.query(
            Dealer.name,
            Dealer.dealer_type,
            State.name.label("state_name"),
            func.count(Order.id).label("order_count"),
            func.coalesce(func.sum(Order.revenue), 0.0).label("revenue"),
        )
        .join(Order, Order.dealer_id == Dealer.id)
        .join(State, Dealer.state_id == State.id)
    )
    if vehicle_type:
        q = q.filter(Order.vehicle_type == vehicle_type)
    rows = q.group_by(Dealer.name, Dealer.dealer_type, State.name).order_by(
        func.sum(Order.revenue).desc()
    ).limit(limit).all()
    return [
        {
            "dealer_name": r.name,
            "dealer_type": r.dealer_type,
            "state_name": r.state_name,
            "order_count": r.order_count,
            "revenue": round(float(r.revenue), 2),
        }
        for r in rows
    ]


def get_profitability_by_state(db: Session, vehicle_type: str | None = None) -> list[dict]:
    from app.core.config import settings

    margin = settings.PROFIT_MARGIN_PCT
    states = get_revenue_by_state(db, vehicle_type)
    return [
        {
            **s,
            "estimated_profit": round(s["revenue"] * margin, 2),
            "margin_pct": margin * 100,
        }
        for s in states
    ]


def get_oem_comparison(db: Session) -> list[dict]:
    new_data = {r["name"]: r for r in get_revenue_by_oem(db, "new")}
    old_data = {r["name"]: r for r in get_revenue_by_oem(db, "old")}
    all_oems = set(new_data) | set(old_data)
    return [
        {
            "oem_name": name,
            "new_revenue": new_data.get(name, {}).get("revenue", 0),
            "old_revenue": old_data.get(name, {}).get("revenue", 0),
            "new_orders": new_data.get(name, {}).get("order_count", 0),
            "old_orders": old_data.get(name, {}).get("order_count", 0),
        }
        for name in sorted(
            all_oems,
            key=lambda n: new_data.get(n, {}).get("revenue", 0) + old_data.get(n, {}).get("revenue", 0),
            reverse=True,
        )
    ]

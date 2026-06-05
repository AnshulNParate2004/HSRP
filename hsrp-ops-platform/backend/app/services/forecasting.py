"""Forecasting — order volume, revenue trends, festival demand, workload."""

from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import Order


def _linear_forecast(values: list[float], periods: int = 4) -> list[dict]:
    """Least-squares trend forecast (numpy when available)."""
    if not values:
        return [{"period": f"+{i+1}", "forecast": 0.0} for i in range(periods)]
    if len(values) < 2:
        avg = values[0]
        return [{"period": f"+{i+1}", "forecast": round(avg, 1)} for i in range(periods)]
    try:
        import numpy as np

        x = np.arange(len(values), dtype=float)
        y = np.array(values, dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        return [
            {
                "period": f"+{i+1}",
                "forecast": round(float(max(0, intercept + slope * (len(values) + i))), 1),
            }
            for i in range(periods)
        ]
    except ImportError:
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n
        num = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        den = sum((i - x_mean) ** 2 for i in range(n)) or 1
        slope = num / den
        intercept = y_mean - slope * x_mean
        return [
            {"period": f"+{i+1}", "forecast": round(max(0, intercept + slope * (n + i)), 1)}
            for i in range(periods)
        ]


def forecast_monthly_orders(db: Session, vehicle_type: str | None = None) -> dict:
    since = datetime.utcnow() - timedelta(days=365)
    q = db.query(Order).filter(Order.order_date >= since)
    if vehicle_type:
        q = q.filter(Order.vehicle_type == vehicle_type)
    orders = q.all()
    buckets: dict[str, int] = {}
    for o in orders:
        key = o.order_date.strftime("%Y-%m")
        buckets[key] = buckets.get(key, 0) + 1
    sorted_keys = sorted(buckets.keys())
    history = [{"period": k, "order_count": buckets[k]} for k in sorted_keys[-6:]]
    forecast = _linear_forecast([float(buckets[k]) for k in sorted_keys[-6:]], 3)
    return {"history": history, "forecast": forecast, "vehicle_type": vehicle_type or "all"}


def forecast_revenue(db: Session) -> dict:
    since = datetime.utcnow() - timedelta(days=180)
    orders = db.query(Order).filter(Order.order_date >= since).all()
    buckets: dict[str, float] = {}
    for o in orders:
        key = o.order_date.strftime("%Y-W%W")
        buckets[key] = buckets.get(key, 0) + o.revenue
    sorted_keys = sorted(buckets.keys())
    history = [{"period": k, "revenue": round(buckets[k], 2)} for k in sorted_keys[-8:]]
    forecast_vals = _linear_forecast([buckets[k] for k in sorted_keys[-8:]], 4)
    return {
        "history": history,
        "forecast": [{"period": f["period"], "revenue": f["forecast"]} for f in forecast_vals],
    }


def festival_demand_forecast(db: Session) -> list[dict]:
    """Festival demand from historical monthly order patterns (data-driven)."""
    from collections import defaultdict
    from app.models.entities import Order

    now = datetime.utcnow()
    monthly: dict[int, list[int]] = defaultdict(list)
    orders = db.query(Order).filter(Order.order_date >= now - timedelta(days=730)).all()
    for o in orders:
        monthly[o.order_date.month].append(1)

    if not monthly:
        return []

    avg_per_month = sum(len(v) for v in monthly.values()) / max(len(monthly), 1)
    results = []
    for month in sorted(monthly.keys()):
        counts = monthly[month]
        avg_count = sum(counts) / len(counts) if counts else 0
        mult = round(avg_count / max(avg_per_month, 1), 2)
        month_name = datetime(2000, month, 1).strftime("%B")
        projected = int(avg_count * 30) if avg_count else 0
        results.append({
            "month": month_name,
            "month_num": month,
            "demand_multiplier": mult,
            "projected_orders": projected,
            "historical_avg_daily": round(avg_count, 1),
            "recommendation": (
                f"Increase stock by {int((mult - 1) * 100)}% before {month_name}"
                if mult > 1.1
                else f"Normal demand expected in {month_name}"
            ),
        })
    return sorted(results, key=lambda x: x["demand_multiplier"], reverse=True)


def predict_workload(db: Session) -> list[dict]:
    """ESO workload forecast from current pending orders vs configured capacity."""
    from app.core.config import settings
    from app.models.entities import ESO, State

    esos = db.query(ESO).filter(ESO.is_active.is_(True)).all()
    results = []
    for eso in esos:
        pending = db.query(Order).filter(
            Order.eso_id == eso.id,
            Order.current_stage.notin_(["completed", "received"]),
        ).count()
        state = db.query(State).filter(State.id == eso.state_id).first()
        capacity = settings.ESO_CAPACITY_ORDERS
        load_pct = round(pending / capacity * 100, 1) if capacity else 0
        results.append({
            "eso_id": eso.id,
            "eso_name": eso.name,
            "state_name": state.name if state else "",
            "pending_orders": pending,
            "load_pct": min(load_pct, 200),
            "status": "overloaded" if load_pct > 100 else "high" if load_pct > 70 else "normal",
        })
    results.sort(key=lambda x: x["load_pct"], reverse=True)
    return results

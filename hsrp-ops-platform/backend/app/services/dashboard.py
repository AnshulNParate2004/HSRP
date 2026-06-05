"""Dashboard aggregation — single summary for executive view."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import Order
from app.services import ai_alerts, pendency_monitor, performance_analytics, tat_analysis
from app.services.vehicle_filter import filter_orders, orders_query


def get_dashboard_summary(db: Session, vehicle_type: str | None = None) -> dict:
    base = orders_query(db, vehicle_type)
    total_orders = base.count()
    total_revenue = float(
        filter_orders(db.query(func.coalesce(func.sum(Order.revenue), 0.0)), vehicle_type).scalar() or 0
    )
    if vehicle_type:
        new_orders = total_orders if vehicle_type == "new" else 0
        old_orders = total_orders if vehicle_type == "old" else 0
    else:
        new_orders = db.query(Order).filter(Order.vehicle_type == "new").count()
        old_orders = db.query(Order).filter(Order.vehicle_type == "old").count()

    pending = pendency_monitor.get_pendency_overview(db, vehicle_type)["total_pending"]
    completed = filter_orders(
        db.query(Order).filter(Order.current_stage == "completed"),
        vehicle_type,
    ).count()
    critical_alerts = len(ai_alerts.get_alerts(db, severity="critical"))
    active = performance_analytics.get_active_counts(db)

    return {
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "new_vehicle_orders": new_orders,
        "old_vehicle_orders": old_orders,
        "pending_orders": pending,
        "completed_orders": completed,
        "critical_alerts": critical_alerts,
        "avg_tat_hours": tat_analysis.get_overall_avg_tat(db, vehicle_type),
        "active_esos": active["active_esos"],
        "active_oems": active["active_oems"],
        "active_dealers": active["active_dealers"],
        "vehicle_type": vehicle_type or "all",
    }

"""AI-based smart alerts — rule engine + Azure OpenAI recommendations."""

from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Alert, ESO, Order, Rejection, State
from app.services import inventory_intelligence, pendency_monitor, performance_analytics
from app.services.llm.azure_client import get_azure_llm
from app.services.llm.recommendations import llm_recommendation


def generate_alerts(db: Session, clear_existing: bool = False) -> list[Alert]:
    """Run all alert rules and persist to DB."""
    if clear_existing:
        db.query(Alert).filter(Alert.is_resolved.is_(False)).delete()
        db.flush()

    new_alerts: list[Alert] = []

    # 1. Stock shortage within 7 days
    for risk in inventory_intelligence.get_shortage_risk(db, horizon_days=7):
        if risk["risk_level"] in ("critical", "high"):
            new_alerts.append(Alert(
                alert_type="stock_shortage",
                severity="critical" if risk["risk_level"] == "critical" else "high",
                title=f"Stock shortage risk: {risk['state_name']} / {risk['oem_name']}",
                message=f"Projected need {risk['projected_need_7d']} vs stock {risk['current_stock']} ({risk['plate_size']})",
                entity_type="inventory",
                entity_id=risk["inventory_id"],
                recommendation=risk["recommendation"],
            ))

    # 2. Critical pendencies (SLA breach)
    for p in pendency_monitor.get_critical_pendencies(db, limit=10):
        new_alerts.append(Alert(
            alert_type="pendency_delay",
            severity="critical" if p["overdue_hours"] > 48 else "high",
            title=f"SLA breach: {p['order_number']}",
            message=f"Stage {p['stage']} overdue by {p['overdue_hours']}h (SLA: {p['sla_hours']}h)",
            entity_type="order",
            entity_id=p["order_id"],
            recommendation=llm_recommendation(
                "pendency_delay",
                p,
                "Escalate to state operations manager and reassign ESO workload",
            ),
        ))

    # 3. Underperforming ESOs (< 70% of state average completion rate)
    eso_perf = performance_analytics.get_eso_performance(db)
    by_state: dict[str, list[float]] = {}
    for e in eso_perf:
        by_state.setdefault(e["state_name"], []).append(e["completion_rate"])
    state_avg = {s: sum(rates) / len(rates) for s, rates in by_state.items() if rates}

    for e in eso_perf:
        avg = state_avg.get(e["state_name"], 100)
        if e["completion_rate"] < avg * 0.7 and e["total_orders"] >= 5:
            new_alerts.append(Alert(
                alert_type="underperforming_eso",
                severity="medium",
                title=f"Underperforming ESO: {e['eso_name']}",
                message=f"Completion rate {e['completion_rate']}% vs state avg {round(avg, 1)}%",
                entity_type="eso",
                entity_id=e["eso_id"],
                recommendation=llm_recommendation(
                    "underperforming_eso",
                    e,
                    "Review embossing capacity and rejection root causes",
                ),
            ))

    # 4. Rejection spike (this week > 2× 4-week average)
    four_weeks_ago = datetime.utcnow() - timedelta(weeks=4)
    one_week_ago = datetime.utcnow() - timedelta(weeks=1)
    esos = db.query(ESO).all()
    for eso in esos:
        total_4w = db.query(Rejection).filter(Rejection.eso_id == eso.id, Rejection.rejected_at >= four_weeks_ago).count()
        recent_1w = db.query(Rejection).filter(Rejection.eso_id == eso.id, Rejection.rejected_at >= one_week_ago).count()
        avg_weekly = total_4w / 4
        if avg_weekly > 0 and recent_1w > avg_weekly * 2:
            new_alerts.append(Alert(
                alert_type="rejection_spike",
                severity="high",
                title=f"Rejection spike at {eso.name}",
                message=f"{recent_1w} rejections this week vs {round(avg_weekly, 1)}/week average",
                entity_type="eso",
                entity_id=eso.id,
                recommendation="Inspect embossing quality controls and plate material batch",
            ))

    # 5. Revenue drop by state (this month < 85% of 3-month avg)
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    three_months_ago = now - timedelta(days=90)
    states = db.query(State).all()
    for state in states:
        rev_3m = (
            db.query(func.coalesce(func.sum(Order.revenue), 0.0))
            .filter(Order.state_id == state.id, Order.order_date >= three_months_ago)
            .scalar()
        ) or 0.0
        rev_month = (
            db.query(func.coalesce(func.sum(Order.revenue), 0.0))
            .filter(Order.state_id == state.id, Order.order_date >= month_start)
            .scalar()
        ) or 0.0
        monthly_avg = rev_3m / 3
        if monthly_avg > 0 and rev_month < monthly_avg * 0.85:
            new_alerts.append(Alert(
                alert_type="revenue_drop",
                severity="medium",
                title=f"Revenue drop: {state.name}",
                message=f"MTD revenue ₹{round(rev_month, 0):,.0f} vs avg ₹{round(monthly_avg, 0):,.0f}",
                entity_type="state",
                entity_id=state.id,
                recommendation="Review OEM order flow and dealer engagement in this state",
            ))

    for alert in new_alerts:
        db.add(alert)
    db.commit()
    return new_alerts


def get_alerts(db: Session, severity: str | None = None, unresolved_only: bool = True) -> list[Alert]:
    q = db.query(Alert)
    if unresolved_only:
        q = q.filter(Alert.is_resolved.is_(False))
    if severity:
        q = q.filter(Alert.severity == severity)
    return q.order_by(Alert.created_at.desc()).all()

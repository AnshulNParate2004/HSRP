"""Build live operational context from database for LLM prompts."""

import json
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services import (
    dashboard,
    inventory_intelligence,
    monitoring,
    pendency_monitor,
    performance_analytics,
    revenue_analytics,
    tat_analysis,
)
from app.services.forecasting import forecast_monthly_orders, predict_workload
from app.models.entities import Portal, Alert


def build_operational_context(db: Session, vehicle_type: str | None = None) -> dict:
    """Aggregate all analytics into one JSON-safe context for the LLM."""
    summary = dashboard.get_dashboard_summary(db)
    return {
        "company": "National HSRP Enterprise (HSRP Ops)",
        "vehicle_filter": vehicle_type or "all",
        "dashboard": summary,
        "revenue": {
            "by_state": revenue_analytics.get_revenue_by_state(db, vehicle_type)[:12],
            "by_oem": revenue_analytics.get_revenue_by_oem(db, vehicle_type)[:10],
            "by_portal": revenue_analytics.get_revenue_by_portal(db),
            "profitability": revenue_analytics.get_profitability_by_state(db, vehicle_type)[:8],
        },
        "pendency": {
            "overview": pendency_monitor.get_pendency_overview(db, vehicle_type),
            "by_stage": pendency_monitor.get_pendency_by_stage(db, vehicle_type),
            "critical": pendency_monitor.get_critical_pendencies(db, limit=8),
        },
        "performance": {
            "active_counts": performance_analytics.get_active_counts(db),
            "eso_bottom": performance_analytics.get_eso_performance(db, vehicle_type)[:8],
            "rejection_trends": performance_analytics.get_rejection_trends(db),
        },
        "inventory": {
            "shortage_risks": inventory_intelligence.get_shortage_risk(db)[:8],
            "low_stock_count": len(
                [i for i in inventory_intelligence.get_inventory_overview(db) if i["status"] != "ok"]
            ),
        },
        "tat": {
            "by_stage": tat_analysis.get_tat_by_stage(db, vehicle_type),
            "overall_avg_hours": tat_analysis.get_overall_avg_tat(db),
        },
        "monitoring": monitoring.get_live_summary(db),
        "forecast": forecast_monthly_orders(db, vehicle_type),
        "eso_workload": predict_workload(db)[:10],
        "portals": [p.name for p in db.query(Portal).all()],
        "open_alerts": [
            {"title": a.title, "severity": a.severity, "message": a.message}
            for a in db.query(Alert).filter(Alert.is_resolved.is_(False)).limit(10).all()
        ],
        "config": {
            "profit_margin_pct": settings.PROFIT_MARGIN_PCT,
            "sla_hours": {
                "issuance": settings.SLA_ISSUANCE_HOURS,
                "embossing": settings.SLA_EMBOSSING_HOURS,
                "dispatch": settings.SLA_DISPATCH_HOURS,
                "fitment": settings.SLA_FITMENT_HOURS,
            },
        },
    }


def context_to_json(db: Session, vehicle_type: str | None = None) -> str:
    return json.dumps(build_operational_context(db, vehicle_type), default=str, indent=2)

"""Platform UI configuration — served to frontend (no hardcoded business data)."""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import ORDER_STAGES
from app.services import dashboard


STAGE_LABELS = {
    "received": "Received",
    "issuance_pending": "Issuance Pending",
    "embossing_pending": "Embossing Pending",
    "dc_pending": "DC Pending",
    "dispatch_pending": "Dispatch Pending",
    "fitment_pending": "Fitment Pending",
    "completed": "Completed",
}


def get_ui_config(db: Session) -> dict:
    return {
        "app": {
            "name": "HSRP Ops",
            "tagline": "HSRP Ops",
            "company": "National HSRP Enterprise",
            "description": "AI-Powered HSRP Operations & Analytics",
        },
        "vehicle_filters": [
            {"value": "all", "label": "All Vehicles"},
            {"value": "new", "label": "New Vehicle"},
            {"value": "old", "label": "Old Vehicle"},
        ],
        "order_stages": [{"key": s, "label": STAGE_LABELS.get(s, s)} for s in ORDER_STAGES],
        "profit_margin_pct": settings.PROFIT_MARGIN_PCT,
        "llm_configured": settings.azure_configured,
        "llm_model": settings.azure_deployment if settings.azure_configured else None,
        "navigation": [
            {"title": "Dashboard", "path": "/app", "icon": "LayoutDashboard"},
            {"title": "Live Monitor", "path": "/app/monitoring", "icon": "Radio"},
            {"title": "Revenue", "path": "/app/revenue", "icon": "IndianRupee"},
            {"title": "Pendency", "path": "/app/pendency", "icon": "Clock"},
            {"title": "Performance", "path": "/app/performance", "icon": "Gauge"},
            {"title": "Inventory", "path": "/app/inventory", "icon": "Package"},
            {"title": "Planning", "path": "/app/planning", "icon": "TrendingUp"},
            {"title": "TAT Analysis", "path": "/app/tat", "icon": "Timer"},
            {"title": "AI Alerts", "path": "/app/alerts", "icon": "Bell"},
            {"title": "AI Assistant", "path": "/app/assistant", "icon": "MessageSquare"},
            {"title": "Reports", "path": "/app/reports", "icon": "FileDown"},
            {"title": "Integrations", "path": "/app/integrations", "icon": "Plug"},
        ],
        "report_exports": [
            {"id": "revenue", "label": "Revenue Analytics (CSV)", "description": "State, OEM, portal breakdown"},
            {"id": "pendency", "label": "Pendency MIS (CSV)", "description": "Stage bottlenecks & SLA breaches"},
            {"id": "performance", "label": "Performance Report (CSV)", "description": "ESO productivity & rejections"},
            {"id": "inventory", "label": "Inventory Report (CSV)", "description": "Stock levels & shortage risk"},
            {"id": "tat", "label": "TAT Analysis (CSV)", "description": "Lifecycle turnaround benchmarks"},
        ],
        "landing_features": [
            {"title": "Revenue Analytics", "description": "State, OEM, and portal-wise contribution", "icon": "BarChart3"},
            {"title": "Pendency Monitor", "description": "Real-time delay and SLA breach tracking", "icon": "Clock"},
            {"title": "Inventory Intelligence", "description": "Stock shortage prediction and replenishment", "icon": "Package"},
            {"title": "AI Assistant", "description": "Azure OpenAI powered operational Q&A", "icon": "Bell"},
        ],
    }


def get_dashboard_metrics(db: Session, vehicle_type: str | None = None) -> list[dict]:
    """Metric card definitions with live values from DB."""
    s = dashboard.get_dashboard_summary(db, vehicle_type)
    metrics = [
        {"key": "total_orders", "label": "Total Orders", "value": s["total_orders"], "format": "number"},
        {"key": "total_revenue", "label": "Total Revenue", "value": s["total_revenue"], "format": "currency"},
        {"key": "pending_orders", "label": "Pending Orders", "value": s["pending_orders"], "format": "number"},
        {"key": "completed_orders", "label": "Completed", "value": s["completed_orders"], "format": "number"},
        {"key": "critical_alerts", "label": "Critical Alerts", "value": s["critical_alerts"], "format": "number"},
        {"key": "avg_tat_hours", "label": "Avg TAT (hrs)", "value": s["avg_tat_hours"], "format": "decimal"},
    ]
    if not vehicle_type:
        metrics.extend([
            {"key": "new_vehicle_orders", "label": "New Vehicles", "value": s["new_vehicle_orders"], "format": "number"},
            {"key": "old_vehicle_orders", "label": "Old Vehicles", "value": s["old_vehicle_orders"], "format": "number"},
        ])
    metrics.extend([
        {"key": "active_esos", "label": "Active ESOs", "value": s["active_esos"], "format": "number"},
        {"key": "active_oems", "label": "Active OEMs", "value": s["active_oems"], "format": "number"},
    ])
    return metrics


def get_monitoring_metrics(db: Session, vehicle_type: str | None = None) -> list[dict]:
    from app.services import monitoring

    live = monitoring.get_live_summary(db, vehicle_type)
    return [
        {"key": "total_active", "label": "Active Orders", "value": live["total_active_orders"], "icon": "Activity"},
        {"key": "new_live", "label": "New Vehicle Live", "value": live["new_vehicle_live"], "icon": "Truck"},
        {"key": "old_live", "label": "Old Vehicle Live", "value": live["old_vehicle_live"], "icon": "Truck"},
        {"key": "embossing", "label": "In Embossing", "value": live["in_embossing"], "icon": "Factory"},
        {"key": "dispatch", "label": "In Dispatch", "value": live["in_dispatch"], "icon": "Truck"},
        {"key": "fitment", "label": "In Fitment", "value": live["in_fitment"], "icon": "Users"},
    ]

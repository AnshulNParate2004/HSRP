"""LangChain tools — each tool queries live backend analytics (no hardcoded answers)."""

import json
from typing import Callable

from langchain_core.tools import StructuredTool
from sqlalchemy.orm import Session

from app.services import (
    dashboard,
    inventory_intelligence,
    pendency_monitor,
    performance_analytics,
    revenue_analytics,
    tat_analysis,
)
from app.services.forecasting import forecast_monthly_orders, festival_demand_forecast


def _json(data) -> str:
    return json.dumps(data, default=str)


def build_analytics_tools(db: Session, vehicle_type: str | None = None) -> list[StructuredTool]:
    """Create LangChain tools bound to the current DB session."""

    def tool_fn(name: str, description: str, fn: Callable[[], object]) -> StructuredTool:
        return StructuredTool.from_function(
            func=lambda: _json(fn()),
            name=name,
            description=description,
        )

    return [
        tool_fn(
            "get_dashboard_summary",
            "PAN India executive KPIs: total orders, revenue, pending, alerts, active ESOs/OEMs.",
            lambda: dashboard.get_dashboard_summary(db),
        ),
        tool_fn(
            "get_revenue_by_state",
            "Revenue and order count breakdown by Indian state.",
            lambda: revenue_analytics.get_revenue_by_state(db, vehicle_type),
        ),
        tool_fn(
            "get_revenue_by_oem",
            "Revenue and order count breakdown by vehicle OEM (Maruti, Hyundai, etc.).",
            lambda: revenue_analytics.get_revenue_by_oem(db, vehicle_type),
        ),
        tool_fn(
            "get_revenue_by_portal",
            "Order source portal contribution: DISHA, Hero Biz, Old Vehicle Portal, POS.",
            lambda: revenue_analytics.get_revenue_by_portal(db),
        ),
        tool_fn(
            "get_dealer_contribution",
            "Dealer and fitment center revenue contribution.",
            lambda: revenue_analytics.get_dealer_contribution(db, vehicle_type),
        ),
        tool_fn(
            "get_pendency_overview",
            "Pending and delayed orders overview with delay rate percentage.",
            lambda: pendency_monitor.get_pendency_overview(db, vehicle_type),
        ),
        tool_fn(
            "get_pendency_by_stage",
            "Pendency counts by lifecycle stage: issuance, embossing, DC, dispatch, fitment.",
            lambda: pendency_monitor.get_pendency_by_stage(db, vehicle_type),
        ),
        tool_fn(
            "get_critical_pendencies",
            "Orders breaching SLA — critical escalation list.",
            lambda: pendency_monitor.get_critical_pendencies(db, limit=15),
        ),
        tool_fn(
            "get_eso_performance",
            "ESO productivity: completion rate, rejections, average TAT per embossing station.",
            lambda: performance_analytics.get_eso_performance(db, vehicle_type),
        ),
        tool_fn(
            "get_inventory_shortage_risk",
            "7-day stock shortage predictions with replenishment recommendations.",
            lambda: inventory_intelligence.get_shortage_risk(db),
        ),
        tool_fn(
            "get_tat_by_stage",
            "Turnaround time averages per HSRP lifecycle stage.",
            lambda: tat_analysis.get_tat_by_stage(db, vehicle_type),
        ),
        tool_fn(
            "forecast_orders",
            "Historical and forecasted monthly order volumes.",
            lambda: forecast_monthly_orders(db, vehicle_type),
        ),
        tool_fn(
            "festival_demand_forecast",
            "Seasonal/festival demand projections for inventory planning.",
            lambda: festival_demand_forecast(db),
        ),
    ]

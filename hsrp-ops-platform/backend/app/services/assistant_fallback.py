"""Rule-based assistant fallback when Azure OpenAI is unavailable."""

from sqlalchemy.orm import Session

from app.services import dashboard, inventory_intelligence, pendency_monitor, performance_analytics, revenue_analytics


def ask(db: Session, question: str) -> dict:
    q = question.strip().lower()
    summary = dashboard.get_dashboard_summary(db)

    if "revenue" in q or "sales" in q:
        oems = revenue_analytics.get_revenue_by_oem(db, limit=1)
        if oems:
            o = oems[0]
            return {
                "answer": f"Top OEM: {o['name']} — ₹{o['revenue']:,.0f} ({o['order_count']} orders).",
                "sources": ["revenue_analytics"],
            }
        return {
            "answer": f"Total revenue: ₹{summary['total_revenue']:,.0f} across {summary['total_orders']} orders.",
            "sources": ["dashboard"],
        }
    if "pendency" in q or "delay" in q:
        p = pendency_monitor.get_pendency_overview(db)
        return {
            "answer": f"{p['total_pending']} pending, {p['total_delayed']} delayed ({p['delay_rate_pct']}% delay rate).",
            "sources": ["pendency_monitor"],
        }
    if "stock" in q or "inventory" in q:
        risks = inventory_intelligence.get_shortage_risk(db)[:1]
        if risks:
            r = risks[0]
            return {"answer": f"Shortage: {r['state_name']}/{r['oem_name']} — {r['recommendation']}", "sources": ["inventory"]}
        return {"answer": "No critical stock shortages detected.", "sources": ["inventory"]}
    if "eso" in q:
        esos = performance_analytics.get_eso_performance(db)[:1]
        if esos:
            e = esos[0]
            return {"answer": f"Lowest completion: {e['eso_name']} at {e['completion_rate']}%.", "sources": ["performance"]}

    return {
        "answer": (
            f"PAN India: {summary['total_orders']} orders, ₹{summary['total_revenue']:,.0f} revenue, "
            f"{summary['pending_orders']} pending, {summary['critical_alerts']} alerts."
        ),
        "sources": ["dashboard"],
    }

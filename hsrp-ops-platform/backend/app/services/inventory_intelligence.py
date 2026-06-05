"""Inventory intelligence — stock levels, consumption, shortage prediction."""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload

from app.models.entities import Inventory, InventoryConsumption, Warehouse


def _avg_daily_consumption(db: Session, inventory_id: int, days: int = 30) -> float:
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(InventoryConsumption)
        .filter(
            InventoryConsumption.inventory_id == inventory_id,
            InventoryConsumption.consumed_at >= since,
        )
        .all()
    )
    if not rows:
        return 0.0
    total = sum(r.quantity for r in rows)
    return total / days


def _stock_status(quantity: int, reorder_level: int, days_of_stock: float | None) -> str:
    if quantity <= reorder_level * 0.5:
        return "critical"
    if quantity <= reorder_level or (days_of_stock is not None and days_of_stock < 7):
        return "low"
    return "ok"


def get_inventory_overview(db: Session) -> list[dict]:
    items = (
        db.query(Inventory)
        .options(
            joinedload(Inventory.warehouse).joinedload(Warehouse.state),
            joinedload(Inventory.oem),
        )
        .all()
    )
    results = []
    for inv in items:
        avg_daily = _avg_daily_consumption(db, inv.id)
        days_of_stock = round(inv.quantity / avg_daily, 1) if avg_daily > 0 else None
        status = _stock_status(inv.quantity, inv.reorder_level, days_of_stock)
        results.append({
            "id": inv.id,
            "warehouse_name": inv.warehouse.name if inv.warehouse else "",
            "state_name": inv.warehouse.state.name if inv.warehouse and inv.warehouse.state else "",
            "oem_name": inv.oem.name if inv.oem else "",
            "plate_size": inv.plate_size,
            "plate_color": inv.plate_color,
            "quantity": inv.quantity,
            "reorder_level": inv.reorder_level,
            "avg_daily_consumption": round(avg_daily, 1),
            "days_of_stock": days_of_stock,
            "status": status,
        })
    return results


def get_consumption_by_state(db: Session) -> list[dict]:
    overview = get_inventory_overview(db)
    by_state: dict[str, dict] = {}
    for item in overview:
        state = item["state_name"]
        if state not in by_state:
            by_state[state] = {"state_name": state, "total_stock": 0, "low_stock_items": 0}
        by_state[state]["total_stock"] += item["quantity"]
        if item["status"] in ("low", "critical"):
            by_state[state]["low_stock_items"] += 1
    return list(by_state.values())


def get_shortage_risk(db: Session, horizon_days: int = 7) -> list[dict]:
    """Predict stock shortages within N days using avg daily consumption."""
    risks = []
    for inv in (
        db.query(Inventory)
        .options(joinedload(Inventory.oem), joinedload(Inventory.warehouse).joinedload(Warehouse.state))
        .all()
    ):
        avg_daily = _avg_daily_consumption(db, inv.id)
        projected_need = int(avg_daily * horizon_days)
        if projected_need > inv.quantity:
            gap = projected_need - inv.quantity
            risk_level = "critical" if gap > inv.reorder_level else "high" if gap > inv.reorder_level * 0.5 else "medium"
            risks.append({
                "inventory_id": inv.id,
                "state_name": inv.warehouse.state.name if inv.warehouse and inv.warehouse.state else "",
                "oem_name": inv.oem.name if inv.oem else "",
                "plate_size": inv.plate_size,
                "plate_color": inv.plate_color,
                "current_stock": inv.quantity,
                "projected_need_7d": projected_need,
                "gap": gap,
                "risk_level": risk_level,
                "recommendation": f"Replenish {gap} units within {horizon_days} days",
            })
    risks.sort(key=lambda x: x["gap"], reverse=True)
    return risks


def get_size_color_breakdown(db: Session) -> dict:
    items = db.query(Inventory).all()
    by_size: dict[str, int] = {}
    by_color: dict[str, int] = {}
    for inv in items:
        by_size[inv.plate_size] = by_size.get(inv.plate_size, 0) + inv.quantity
        by_color[inv.plate_color] = by_color.get(inv.plate_color, 0) + inv.quantity
    return {
        "by_size": [{"size": k, "quantity": v} for k, v in sorted(by_size.items())],
        "by_color": [{"color": k, "quantity": v} for k, v in sorted(by_color.items())],
    }


def get_oem_consumption(db: Session) -> list[dict]:
    from sqlalchemy import func
    from app.models.entities import OEM

    rows = (
        db.query(
            OEM.name,
            func.sum(InventoryConsumption.quantity).label("consumed"),
        )
        .join(Inventory, Inventory.oem_id == OEM.id)
        .join(InventoryConsumption, InventoryConsumption.inventory_id == Inventory.id)
        .group_by(OEM.name)
        .order_by(func.sum(InventoryConsumption.quantity).desc())
        .all()
    )
    return [{"oem_name": r.name, "consumed_units": int(r.consumed or 0)} for r in rows]


def get_historical_consumption(db: Session, weeks: int = 12) -> list[dict]:
    since = datetime.utcnow() - timedelta(weeks=weeks)
    rows = (
        db.query(InventoryConsumption)
        .filter(InventoryConsumption.consumed_at >= since)
        .order_by(InventoryConsumption.consumed_at)
        .all()
    )
    buckets: dict[str, int] = {}
    for r in rows:
        key = r.consumed_at.strftime("%Y-W%W")
        buckets[key] = buckets.get(key, 0) + r.quantity
    return [{"period": k, "consumed": v} for k, v in sorted(buckets.items())]


def get_interstate_balancing(db: Session) -> list[dict]:
    by_state = get_consumption_by_state(db)
    if not by_state:
        return []
    avg_stock = sum(s["total_stock"] for s in by_state) / len(by_state)
    recommendations = []
    surplus = [s for s in by_state if s["total_stock"] > avg_stock * 1.3]
    deficit = [s for s in by_state if s["low_stock_items"] > 0 or s["total_stock"] < avg_stock * 0.7]
    for d in deficit[:5]:
        for s in surplus[:3]:
            transfer = min(int((s["total_stock"] - avg_stock) * 0.2), 200)
            if transfer > 0:
                recommendations.append({
                    "from_state": s["state_name"],
                    "to_state": d["state_name"],
                    "suggested_transfer_units": transfer,
                    "reason": f"{d['state_name']} has {d['low_stock_items']} low-stock SKUs",
                })
    return recommendations[:10]


def get_procurement_plan(db: Session) -> list[dict]:
    plan = []
    for risk in get_shortage_risk(db):
        plan.append({
            "state_name": risk["state_name"],
            "oem_name": risk["oem_name"],
            "plate_size": risk["plate_size"],
            "order_quantity": risk["gap"],
            "priority": risk["risk_level"],
            "timeline_days": 7,
        })
    for item in get_inventory_overview(db):
        if item["status"] == "critical":
            plan.append({
                "state_name": item["state_name"],
                "oem_name": item["oem_name"],
                "plate_size": item["plate_size"],
                "order_quantity": item["reorder_level"],
                "priority": "critical",
                "timeline_days": 3,
            })
    return plan[:25]

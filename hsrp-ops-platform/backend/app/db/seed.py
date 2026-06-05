"""Seed PAN-India demo data — development/staging only."""

import random

from app.core.config import settings
from datetime import datetime, timedelta

from app.db.session import Base, SessionLocal, engine
from app.models.entities import (
    Alert,
    Dealer,
    ESO,
    Inventory,
    InventoryConsumption,
    OEM,
    Order,
    OrderStageHistory,
    Portal,
    Rejection,
    State,
    Warehouse,
)

STATES = [
    ("Maharashtra", "MH"), ("Karnataka", "KA"), ("Tamil Nadu", "TN"),
    ("Gujarat", "GJ"), ("Rajasthan", "RJ"), ("Uttar Pradesh", "UP"),
    ("Delhi", "DL"), ("West Bengal", "WB"), ("Telangana", "TS"),
    ("Kerala", "KL"), ("Punjab", "PB"), ("Haryana", "HR"),
]

OEMS = [
    "Maruti Suzuki", "Hyundai", "Tata Motors", "Mahindra", "Honda",
    "Toyota", "Kia", "Hero MotoCorp", "Bajaj Auto", "TVS Motor",
]

PORTALS = ["DISHA", "Hero Biz", "Old Vehicle Portal", "POS Systems"]

STAGES = [
    "received", "issuance_pending", "embossing_pending",
    "dc_pending", "dispatch_pending", "fitment_pending", "completed",
]

PLATE_SIZES = ["Standard", "Compact", "Commercial"]
PLATE_COLORS = ["White", "Yellow", "Green", "Blue"]


def _random_date(days_back: int = 120) -> datetime:
    return datetime.utcnow() - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
    )


def seed() -> None:
    if settings.is_production and not settings.AUTO_SEED_DEMO:
        raise RuntimeError(
            "Demo seed is disabled in production. Set AUTO_SEED_DEMO=true only on staging."
        )
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        states = [State(name=n, code=c) for n, c in STATES]
        db.add_all(states)
        db.flush()

        oems = [OEM(name=n) for n in OEMS]
        db.add_all(oems)
        portals = [Portal(name=n) for n in PORTALS]
        db.add_all(portals)
        db.flush()

        esos: list[ESO] = []
        dealers: list[Dealer] = []
        warehouses: list[Warehouse] = []
        for state in states:
            for i in range(random.randint(2, 4)):
                esos.append(ESO(name=f"{state.code}-ESO-{i+1}", state_id=state.id))
            for i in range(random.randint(3, 6)):
                dealers.append(Dealer(
                    name=f"{state.name} Dealer {i+1}",
                    state_id=state.id,
                    dealer_type=random.choice(["dealer", "fitment"]),
                ))
            warehouses.append(Warehouse(name=f"{state.name} WH", state_id=state.id))
        db.add_all(esos + dealers + warehouses)
        db.flush()

        # Inventory
        inventory_items: list[Inventory] = []
        for wh in warehouses:
            state_oems = random.sample(oems, k=min(4, len(oems)))
            for oem in state_oems:
                for size in random.sample(PLATE_SIZES, 2):
                    for color in random.sample(PLATE_COLORS, 2):
                        qty = random.randint(50, 800)
                        inv = Inventory(
                            warehouse_id=wh.id,
                            oem_id=oem.id,
                            plate_size=size,
                            plate_color=color,
                            quantity=qty,
                            reorder_level=random.randint(80, 200),
                        )
                        inventory_items.append(inv)
        db.add_all(inventory_items)
        db.flush()

        for inv in inventory_items:
            for _ in range(random.randint(15, 40)):
                db.add(InventoryConsumption(
                    inventory_id=inv.id,
                    consumed_at=_random_date(60),
                    quantity=random.randint(5, 40),
                ))

        # Orders
        orders: list[Order] = []
        for i in range(500):
            state = random.choice(states)
            state_esos = [e for e in esos if e.state_id == state.id]
            state_dealers = [d for d in dealers if d.state_id == state.id]
            stage = random.choices(
                STAGES,
                weights=[5, 15, 20, 10, 15, 15, 20],
            )[0]
            order_date = _random_date(90)
            stage_entered = order_date + timedelta(hours=random.randint(1, 200))
            vehicle_type = random.choice(["new", "new", "new", "old"])
            order = Order(
                order_number=f"HSRP-{state.code}-{10000 + i}",
                vehicle_type=vehicle_type,
                oem_id=random.choice(oems).id,
                state_id=state.id,
                eso_id=random.choice(state_esos).id if state_esos else None,
                dealer_id=random.choice(state_dealers).id if state_dealers else None,
                portal_id=random.choice(portals).id,
                revenue=round(random.uniform(800, 3500), 2),
                current_stage=stage,
                order_date=order_date,
                stage_entered_at=stage_entered if stage != "completed" else order_date,
                completed_at=order_date + timedelta(days=random.randint(3, 14)) if stage == "completed" else None,
            )
            orders.append(order)
        db.add_all(orders)
        db.flush()

        # Stage history + rejections
        for order in orders:
            elapsed = order.order_date
            for idx, stage in enumerate(STAGES):
                if stage == order.current_stage:
                    hours = random.uniform(4, 72)
                    db.add(OrderStageHistory(
                        order_id=order.id,
                        stage=stage,
                        entered_at=elapsed,
                        exited_at=None,
                        tat_hours=None,
                    ))
                    break
                hours = random.uniform(2, 48)
                exited = elapsed + timedelta(hours=hours)
                db.add(OrderStageHistory(
                    order_id=order.id,
                    stage=stage,
                    entered_at=elapsed,
                    exited_at=exited,
                    tat_hours=round(hours, 1),
                ))
                elapsed = exited

            if random.random() < 0.08 and order.eso_id:
                db.add(Rejection(
                    order_id=order.id,
                    eso_id=order.eso_id,
                    reason=random.choice([
                        "Embossing defect", "Material quality issue",
                        "Alignment error", "Color mismatch",
                    ]),
                    rejected_at=order.order_date + timedelta(days=random.randint(1, 5)),
                ))

        db.commit()
        print(f"Seeded: {len(states)} states, {len(oems)} OEMs, {len(orders)} orders, {len(inventory_items)} inventory SKUs")

        # Generate AI alerts
        from app.services.ai_alerts import generate_alerts
        alerts = generate_alerts(db)
        print(f"Generated {len(alerts)} AI alerts")

    finally:
        db.close()


if __name__ == "__main__":
    seed()

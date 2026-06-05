from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.entities import Order
from app.schemas.analytics import OrderOut

router = APIRouter()


@router.get("", response_model=list[OrderOut])
def list_orders(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    stage: str | None = None,
    state_id: int | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = (
        db.query(Order)
        .options(
            joinedload(Order.oem),
            joinedload(Order.state),
            joinedload(Order.eso),
            joinedload(Order.portal),
        )
    )
    if vehicle_type:
        q = q.filter(Order.vehicle_type == vehicle_type)
    if stage:
        q = q.filter(Order.current_stage == stage)
    if state_id:
        q = q.filter(Order.state_id == state_id)
    orders = q.order_by(Order.order_date.desc()).limit(limit).all()
    now = datetime.utcnow()
    return [
        OrderOut(
            id=o.id,
            order_number=o.order_number,
            vehicle_type=o.vehicle_type,
            oem_name=o.oem.name if o.oem else "",
            state_name=o.state.name if o.state else "",
            eso_name=o.eso.name if o.eso else None,
            portal_name=o.portal.name if o.portal else "",
            revenue=o.revenue,
            current_stage=o.current_stage,
            order_date=o.order_date,
            hours_in_current_stage=round((now - o.stage_entered_at).total_seconds() / 3600, 1),
        )
        for o in orders
    ]

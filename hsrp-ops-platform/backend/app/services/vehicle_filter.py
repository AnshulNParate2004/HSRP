"""Shared new / old vehicle filtering for analytics."""

from sqlalchemy.orm import Query, Session

from app.models.entities import Order


def filter_orders(q: Query, vehicle_type: str | None) -> Query:
    if vehicle_type in ("new", "old"):
        return q.filter(Order.vehicle_type == vehicle_type)
    return q


def orders_query(db: Session, vehicle_type: str | None = None) -> Query:
    return filter_orders(db.query(Order), vehicle_type)

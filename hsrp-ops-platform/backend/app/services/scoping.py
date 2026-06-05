"""PAN-India vs state-scoped data access for RBAC."""

from sqlalchemy.orm import Query

from app.models.entities import Order


def get_state_filter_ids(allowed_state_ids: list[int] | None) -> list[int] | None:
    """None = all states; [] = no access."""
    return allowed_state_ids


def scope_orders_query(query: Query, state_ids: list[int] | None) -> Query:
    if state_ids is None:
        return query
    if not state_ids:
        return query.filter(False)
    return query.filter(Order.state_id.in_(state_ids))

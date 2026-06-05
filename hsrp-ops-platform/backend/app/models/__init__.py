"""Import all ORM models so metadata is complete for create_all / migrations."""

from app.models.entities import (  # noqa: F401
    Alert,
    AuditLog,
    Dealer,
    ESO,
    Inventory,
    InventoryConsumption,
    OEM,
    Order,
    OrderStageHistory,
    Portal,
    PortalSyncLog,
    Rejection,
    State,
    User,
    Warehouse,
)

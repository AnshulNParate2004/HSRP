from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

ORDER_STAGES = (
    "received",
    "issuance_pending",
    "embossing_pending",
    "dc_pending",
    "dispatch_pending",
    "fitment_pending",
    "completed",
)


class State(Base):
    __tablename__ = "states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)


class OEM(Base):
    __tablename__ = "oems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Portal(Base):
    __tablename__ = "portals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)


class ESO(Base):
    __tablename__ = "esos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    state_id: Mapped[int] = mapped_column(ForeignKey("states.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    state: Mapped["State"] = relationship("State")


class Dealer(Base):
    __tablename__ = "dealers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    state_id: Mapped[int] = mapped_column(ForeignKey("states.id"), nullable=False)
    dealer_type: Mapped[str] = mapped_column(String(20), default="dealer")  # dealer | fitment
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    state: Mapped["State"] = relationship("State")


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    state_id: Mapped[int] = mapped_column(ForeignKey("states.id"), nullable=False)

    state: Mapped["State"] = relationship("State")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    vehicle_type: Mapped[str] = mapped_column(String(10), nullable=False)  # new | old
    oem_id: Mapped[int] = mapped_column(ForeignKey("oems.id"), nullable=False)
    state_id: Mapped[int] = mapped_column(ForeignKey("states.id"), nullable=False)
    eso_id: Mapped[int | None] = mapped_column(ForeignKey("esos.id"), nullable=True)
    dealer_id: Mapped[int | None] = mapped_column(ForeignKey("dealers.id"), nullable=True)
    portal_id: Mapped[int] = mapped_column(ForeignKey("portals.id"), nullable=False)
    revenue: Mapped[float] = mapped_column(Float, default=0.0)
    current_stage: Mapped[str] = mapped_column(String(30), nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    stage_entered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    oem: Mapped["OEM"] = relationship("OEM")
    state: Mapped["State"] = relationship("State")
    eso: Mapped["ESO | None"] = relationship("ESO")
    dealer: Mapped["Dealer | None"] = relationship("Dealer")
    portal: Mapped["Portal"] = relationship("Portal")
    stage_history: Mapped[list["OrderStageHistory"]] = relationship(
        "OrderStageHistory", back_populates="order"
    )
    rejections: Mapped[list["Rejection"]] = relationship("Rejection", back_populates="order")


class OrderStageHistory(Base):
    __tablename__ = "order_stage_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    stage: Mapped[str] = mapped_column(String(30), nullable=False)
    entered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    exited_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tat_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="stage_history")


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)
    oem_id: Mapped[int] = mapped_column(ForeignKey("oems.id"), nullable=False)
    plate_size: Mapped[str] = mapped_column(String(20), nullable=False)
    plate_color: Mapped[str] = mapped_column(String(30), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, default=100)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    warehouse: Mapped["Warehouse"] = relationship("Warehouse")
    oem: Mapped["OEM"] = relationship("OEM")
    consumption: Mapped[list["InventoryConsumption"]] = relationship(
        "InventoryConsumption", back_populates="inventory"
    )


class InventoryConsumption(Base):
    __tablename__ = "inventory_consumption"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inventory_id: Mapped[int] = mapped_column(ForeignKey("inventory.id"), nullable=False)
    consumed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="consumption")


class Rejection(Base):
    __tablename__ = "rejections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    eso_id: Mapped[int] = mapped_column(ForeignKey("esos.id"), nullable=False)
    reason: Mapped[str] = mapped_column(String(200), nullable=False)
    rejected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="rejections")
    eso: Mapped["ESO"] = relationship("ESO")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # low | medium | high | critical
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(40), nullable=False, default="operations_manager")
    # JSON list of state IDs; null = all states (PAN India)
    allowed_state_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    resource: Mapped[str] = mapped_column(String(80), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PortalSyncLog(Base):
    __tablename__ = "portal_sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    portal_name: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success | failed | skipped
    records_fetched: Mapped[int] = mapped_column(Integer, default=0)
    records_upserted: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

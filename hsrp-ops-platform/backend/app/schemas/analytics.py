from datetime import datetime
from pydantic import BaseModel


class MetricItem(BaseModel):
    label: str
    value: float | int
    unit: str | None = None


class BreakdownItem(BaseModel):
    id: int | None = None
    name: str
    order_count: int
    revenue: float
    percentage: float | None = None


class TrendPoint(BaseModel):
    period: str
    order_count: int
    revenue: float


class StagePendency(BaseModel):
    stage: str
    pending_count: int
    delayed_count: int
    avg_hours_in_stage: float


class DashboardSummary(BaseModel):
    total_orders: int
    total_revenue: float
    new_vehicle_orders: int
    old_vehicle_orders: int
    pending_orders: int
    completed_orders: int
    critical_alerts: int
    avg_tat_hours: float
    active_esos: int
    active_oems: int


class AlertOut(BaseModel):
    id: int
    alert_type: str
    severity: str
    title: str
    message: str
    recommendation: str | None
    entity_type: str | None
    entity_id: int | None
    is_resolved: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    order_number: str
    vehicle_type: str
    oem_name: str
    state_name: str
    eso_name: str | None
    portal_name: str
    revenue: float
    current_stage: str
    order_date: datetime
    hours_in_current_stage: float

    model_config = {"from_attributes": True}


class ESOPerformance(BaseModel):
    eso_id: int
    eso_name: str
    state_name: str
    total_orders: int
    completed_orders: int
    completion_rate: float
    rejection_count: int
    avg_tat_hours: float


class InventoryItem(BaseModel):
    id: int
    warehouse_name: str
    state_name: str
    oem_name: str
    plate_size: str
    plate_color: str
    quantity: int
    reorder_level: int
    days_of_stock: float | None
    status: str  # ok | low | critical


class TATStageBreakdown(BaseModel):
    stage: str
    avg_hours: float
    p90_hours: float
    sample_count: int


class ShortageRisk(BaseModel):
    inventory_id: int
    state_name: str
    oem_name: str
    plate_size: str
    current_stock: int
    projected_need_7d: int
    risk_level: str

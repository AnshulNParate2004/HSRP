"""OEM portal integration adapters — live order sync."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PortalOrderPayload:
    external_id: str
    order_number: str
    vehicle_type: str
    oem_name: str
    state_code: str
    portal_name: str
    revenue: float
    current_stage: str
    order_date: datetime
    dealer_name: str | None = None


class PortalAdapter(ABC):
    portal_name: str

    @abstractmethod
    def is_configured(self) -> bool:
        ...

    @abstractmethod
    def fetch_orders(self, since: datetime | None = None) -> list[PortalOrderPayload]:
        ...

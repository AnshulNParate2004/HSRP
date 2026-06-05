"""HTTP JSON portal adapter — works with DISHA, Hero Biz, and similar REST feeds."""

from datetime import datetime

import httpx

from app.core.config import settings
from app.services.integrations.base import PortalAdapter, PortalOrderPayload


class HttpJsonPortalAdapter(PortalAdapter):
    def __init__(self, portal_name: str, api_url: str | None, api_key: str | None):
        self.portal_name = portal_name
        self.api_url = api_url
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.api_url and self.api_key)

    def fetch_orders(self, since: datetime | None = None) -> list[PortalOrderPayload]:
        if not self.is_configured():
            return []
        params = {}
        if since:
            params["since"] = since.isoformat()
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        with httpx.Client(timeout=settings.PORTAL_SYNC_TIMEOUT_SECONDS) as client:
            response = client.get(self.api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
        rows = data if isinstance(data, list) else data.get("orders", data.get("data", []))
        return [_parse_row(row, self.portal_name) for row in rows if isinstance(row, dict)]


def _parse_row(row: dict, portal_name: str) -> PortalOrderPayload:
    order_date = row.get("order_date") or row.get("created_at")
    if isinstance(order_date, str):
        order_date = datetime.fromisoformat(order_date.replace("Z", "+00:00"))
    elif not isinstance(order_date, datetime):
        order_date = datetime.utcnow()
    return PortalOrderPayload(
        external_id=str(row.get("external_id") or row.get("id") or row["order_number"]),
        order_number=str(row["order_number"]),
        vehicle_type=str(row.get("vehicle_type", "new")).lower(),
        oem_name=str(row.get("oem_name") or row.get("oem", "Unknown")),
        state_code=str(row.get("state_code") or row.get("state", "MH")),
        portal_name=portal_name,
        revenue=float(row.get("revenue", 0)),
        current_stage=str(row.get("current_stage", "received")),
        order_date=order_date,
        dealer_name=row.get("dealer_name"),
    )

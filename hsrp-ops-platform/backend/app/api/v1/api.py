from fastapi import APIRouter, Depends

from app.api.v1.endpoints import (
    admin,
    alerts,
    assistant,
    auth,
    config,
    dashboard,
    integrations,
    inventory,
    monitoring,
    orders,
    pendency,
    performance,
    planning,
    reports,
    revenue,
    tat,
)
from app.core.deps import get_current_user

public_router = APIRouter()
public_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

protected_router = APIRouter(dependencies=[Depends(get_current_user)])
protected_router.include_router(config.router, prefix="/config", tags=["Platform Config"])
protected_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
protected_router.include_router(revenue.router, prefix="/revenue", tags=["Revenue Analytics"])
protected_router.include_router(pendency.router, prefix="/pendency", tags=["Pendency Monitor"])
protected_router.include_router(performance.router, prefix="/performance", tags=["Performance"])
protected_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
protected_router.include_router(tat.router, prefix="/tat", tags=["TAT Analysis"])
protected_router.include_router(alerts.router, prefix="/alerts", tags=["AI Alerts"])
protected_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
protected_router.include_router(monitoring.router, prefix="/monitoring", tags=["Real-Time Monitoring"])
protected_router.include_router(assistant.router, prefix="/assistant", tags=["AI Assistant"])
protected_router.include_router(reports.router, prefix="/reports", tags=["Reports & MIS"])
protected_router.include_router(planning.router, prefix="/planning", tags=["Predictive Planning"])
protected_router.include_router(integrations.router, prefix="/integrations", tags=["OEM Integrations"])
protected_router.include_router(admin.router, prefix="/admin", tags=["Administration"])

api_router = APIRouter()
api_router.include_router(public_router)
api_router.include_router(protected_router)

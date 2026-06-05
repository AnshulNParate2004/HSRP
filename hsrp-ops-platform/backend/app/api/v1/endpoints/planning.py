from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import forecasting, inventory_intelligence

router = APIRouter()


@router.get("/forecast/orders")
def forecast_orders(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return forecasting.forecast_monthly_orders(db, vehicle_type)


@router.get("/forecast/revenue")
def forecast_revenue(db: Session = Depends(get_db)):
    return forecasting.forecast_revenue(db)


@router.get("/forecast/festival")
def festival_forecast(db: Session = Depends(get_db)):
    return forecasting.festival_demand_forecast(db)


@router.get("/workload")
def workload(db: Session = Depends(get_db)):
    return forecasting.predict_workload(db)


@router.get("/procurement")
def procurement(db: Session = Depends(get_db)):
    return inventory_intelligence.get_procurement_plan(db)


@router.get("/interstate-balancing")
def interstate(db: Session = Depends(get_db)):
    return inventory_intelligence.get_interstate_balancing(db)


@router.get("/minimum-stock-alerts")
def min_stock(db: Session = Depends(get_db)):
    items = inventory_intelligence.get_inventory_overview(db)
    return [i for i in items if i["status"] in ("low", "critical")]

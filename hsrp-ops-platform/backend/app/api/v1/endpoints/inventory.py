from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import inventory_intelligence

router = APIRouter()


@router.get("/overview")
def inventory_overview(db: Session = Depends(get_db)):
    return inventory_intelligence.get_inventory_overview(db)


@router.get("/by-state")
def consumption_by_state(db: Session = Depends(get_db)):
    return inventory_intelligence.get_consumption_by_state(db)


@router.get("/shortage-risk")
def shortage_risk(db: Session = Depends(get_db)):
    return inventory_intelligence.get_shortage_risk(db)


@router.get("/breakdown")
def size_color_breakdown(db: Session = Depends(get_db)):
    return inventory_intelligence.get_size_color_breakdown(db)


@router.get("/oem-consumption")
def oem_consumption(db: Session = Depends(get_db)):
    return inventory_intelligence.get_oem_consumption(db)


@router.get("/historical-consumption")
def historical_consumption(db: Session = Depends(get_db)):
    return inventory_intelligence.get_historical_consumption(db)

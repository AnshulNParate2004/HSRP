from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.core.deps import require_min_role
from app.db.session import get_db
from app.services import reports_export

router = APIRouter()


@router.get("/summary")
def management_summary(db: Session = Depends(get_db)):
    return reports_export.get_management_summary(db)


@router.get("/export/revenue", response_class=PlainTextResponse)
def export_revenue(
    vehicle_type: str | None = Query(None, pattern="^(new|old)$"),
    db: Session = Depends(get_db),
):
    return PlainTextResponse(
        reports_export.export_revenue_report(db, vehicle_type),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=revenue_report.csv"},
    )


@router.get("/export/pendency", response_class=PlainTextResponse)
def export_pendency(db: Session = Depends(get_db)):
    return PlainTextResponse(
        reports_export.export_pendency_report(db),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pendency_report.csv"},
    )


@router.get("/export/performance", response_class=PlainTextResponse)
def export_performance(db: Session = Depends(get_db)):
    return PlainTextResponse(
        reports_export.export_performance_report(db),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=performance_report.csv"},
    )


@router.get("/export/inventory", response_class=PlainTextResponse)
def export_inventory(db: Session = Depends(get_db)):
    return PlainTextResponse(
        reports_export.export_inventory_report(db),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventory_report.csv"},
    )


@router.get("/export/tat", response_class=PlainTextResponse)
def export_tat(db: Session = Depends(get_db)):
    return PlainTextResponse(
        reports_export.export_tat_report(db),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tat_report.csv"},
    )


@router.get("/export/executive-ppt")
def export_executive_ppt(
    db: Session = Depends(get_db),
    _: None = Depends(require_min_role("executive")),
):
    content = reports_export.export_executive_ppt(db)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": "attachment; filename=hsrp_executive_summary.pptx"},
    )

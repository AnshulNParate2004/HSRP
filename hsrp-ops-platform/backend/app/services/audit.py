from sqlalchemy.orm import Session

from app.models.entities import AuditLog


def log_audit(
    db: Session,
    *,
    user_id: int | None,
    action: str,
    resource: str,
    detail: str | None = None,
    ip_address: str | None = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            detail=detail,
            ip_address=ip_address,
        )
    )
    db.commit()

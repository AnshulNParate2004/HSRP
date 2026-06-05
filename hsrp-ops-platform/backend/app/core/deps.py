import json
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.entities import User
from app.services.audit import log_audit

security_scheme = HTTPBearer(auto_error=False)

ROLE_HIERARCHY = {
    "admin": 100,
    "executive": 80,
    "operations_manager": 60,
    "state_manager": 40,
    "viewer": 20,
}


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.email == payload["sub"], User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    request.state.user = user
    return user


def get_optional_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> User | None:
    if not credentials or not credentials.credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    return db.query(User).filter(User.email == payload["sub"], User.is_active.is_(True)).first()


def require_roles(*roles: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role == "admin":
            return user
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return checker


def require_min_role(min_role: str):
    min_level = ROLE_HIERARCHY.get(min_role, 0)

    def checker(user: User = Depends(get_current_user)) -> User:
        if ROLE_HIERARCHY.get(user.role, 0) < min_level and user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return checker


def get_user_state_ids(user: User) -> list[int] | None:
    """None = all states; empty list = no access."""
    if not user.allowed_state_ids:
        return None
    try:
        ids = json.loads(user.allowed_state_ids)
        return [int(x) for x in ids] if ids else []
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def audit_action(resource: str, action: str):
    def dependency(
        request: Request,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        log_audit(
            db,
            user_id=user.id,
            action=action,
            resource=resource,
            detail=None,
            ip_address=request.client.host if request.client else None,
        )
        return user

    return dependency


CurrentUser = Annotated[User, Depends(get_current_user)]

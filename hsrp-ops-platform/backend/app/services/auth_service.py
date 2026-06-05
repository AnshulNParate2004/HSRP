import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.entities import User
from app.services.audit import log_audit


def bootstrap_admin(db: Session) -> User | None:
    if db.query(User).count() > 0:
        return None
    user = User(
        email=settings.BOOTSTRAP_ADMIN_EMAIL,
        hashed_password=hash_password(settings.BOOTSTRAP_ADMIN_PASSWORD),
        full_name="Platform Administrator",
        role="admin",
        allowed_state_ids=None,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email.lower().strip(), User.is_active.is_(True)).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    user.last_login_at = datetime.utcnow()
    db.commit()
    return user


def login(db: Session, email: str, password: str, ip_address: str | None = None) -> dict | None:
    user = authenticate(db, email, password)
    if not user:
        return None
    token = create_access_token(
        user.email,
        extra={"role": user.role, "user_id": user.id},
    )
    log_audit(db, user_id=user.id, action="login", resource="auth", ip_address=ip_address)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_to_dict(user),
    }


def user_to_dict(user: User) -> dict:
    state_ids = None
    if user.allowed_state_ids:
        try:
            state_ids = json.loads(user.allowed_state_ids)
        except json.JSONDecodeError:
            state_ids = None
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "allowed_state_ids": state_ids,
    }


def create_user(
    db: Session,
    *,
    email: str,
    password: str,
    full_name: str,
    role: str,
    allowed_state_ids: list[int] | None,
    actor: User,
) -> User:
    if actor.role != "admin":
        raise PermissionError("Only admins can create users")
    user = User(
        email=email.lower().strip(),
        hashed_password=hash_password(password),
        full_name=full_name,
        role=role,
        allowed_state_ids=json.dumps(allowed_state_ids) if allowed_state_ids else None,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

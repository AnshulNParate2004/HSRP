from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser, require_roles
from app.db.session import get_db
from app.services import auth_service
from app.services.audit import log_audit

router = APIRouter()


@router.get("/platform-info")
def platform_info():
    """Public branding for login page (no auth required)."""
    return {
        "app": {
            "name": "Real Mazon",
            "tagline": "HSRP Ops",
            "company": "Real Industries Limited",
        }
    }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=120)
    role: str = Field(pattern="^(admin|executive|operations_manager|state_manager|viewer)$")
    allowed_state_ids: list[int] | None = None


@router.post("/login")
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    result = auth_service.login(
        db,
        body.email,
        body.password,
        ip_address=request.client.host if request.client else None,
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return result


@router.get("/me")
def me(user: CurrentUser):
    return auth_service.user_to_dict(user)


@router.post("/users", dependencies=[Depends(require_roles("admin"))])
def create_user(body: CreateUserRequest, user: CurrentUser, db: Session = Depends(get_db)):
    try:
        created = auth_service.create_user(
            db,
            email=body.email,
            password=body.password,
            full_name=body.full_name,
            role=body.role,
            allowed_state_ids=body.allowed_state_ids,
            actor=user,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    log_audit(db, user_id=user.id, action="create_user", resource="users", detail=created.email)
    return auth_service.user_to_dict(created)


@router.get("/users", dependencies=[Depends(require_roles("admin"))])
def list_users(db: Session = Depends(get_db)):
    from app.models.entities import User

    users = db.query(User).order_by(User.email).all()
    return [auth_service.user_to_dict(u) for u in users]

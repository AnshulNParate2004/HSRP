import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.v1.api import api_router
from app.api.v1.endpoints import ws
from app.core.config import settings
from app.core.scheduler import start_scheduler, stop_scheduler
from app.db.session import Base, SessionLocal, engine
import app.models  # noqa: F401 — register all ORM tables
from app.models.entities import Order
from app.services.auth_service import bootstrap_admin

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)


def _maybe_seed_database() -> None:
    if not settings.AUTO_SEED_DEMO:
        return
    db = SessionLocal()
    try:
        if db.query(Order).count() == 0:
            from app.db.seed import seed

            seed()
            logger.info("Seeded demo HSRP data (development only)")
    finally:
        db.close()


def _bootstrap() -> None:
    db = SessionLocal()
    try:
        admin = bootstrap_admin(db)
        if admin:
            logger.warning(
                "Bootstrap admin created: %s — change password immediately",
                admin.email,
            )
    finally:
        db.close()


def _mount_frontend(app: FastAPI) -> None:
    dist = settings.frontend_dist_path
    if not settings.SERVE_FRONTEND or not dist.is_dir() or not (dist / "index.html").is_file():
        logger.info("Frontend not served (build missing at %s)", dist)
        return

    assets_dir = dist / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/", include_in_schema=False)
    async def spa_index():
        return FileResponse(dist / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        file_path = dist / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist / "index.html")

    logger.info("Serving frontend from %s", dist)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    from app.db.upgrade import run_schema_upgrades

    run_schema_upgrades()
    _bootstrap()
    _maybe_seed_database()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production HSRP Operations & Analytics API — National HSRP Enterprise",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(ws.router, prefix=f"{settings.API_V1_PREFIX}/ws", tags=["WebSocket"])


@app.get("/api")
async def api_root():
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else None,
    }


@app.get("/health")
async def health():
    db_ok = False
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_ok = True
    except Exception as exc:
        logger.error("Health check DB failed: %s", exc)
    status_code = 200 if db_ok else 503
    body = {
        "status": "healthy" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }
    return JSONResponse(body, status_code=status_code)


_mount_frontend(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
    )

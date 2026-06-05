from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_APP_DIR = Path(__file__).resolve().parents[1]
_DEFAULT_FRONTEND_DIST = _BACKEND_DIR.parent / "frontend" / "dist"

_ENV_FILES = [
    _BACKEND_DIR / ".env",
    _APP_DIR / ".env",
]


class Settings(BaseSettings):
    APP_NAME: str = "HSRP Operations & Analytics API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./hsrp_ops.db"
    SERVE_FRONTEND: bool = True
    FRONTEND_DIST: str = str(_DEFAULT_FRONTEND_DIST)

    # Production behaviour
    AUTO_SEED_DEMO: bool = False
    BOOTSTRAP_ADMIN_EMAIL: str = "admin@realindustries.in"
    BOOTSTRAP_ADMIN_PASSWORD: str = "ChangeMe@2026!"
    SCHEDULER_ENABLED: bool = True
    ALERT_JOB_INTERVAL_MINUTES: int = 15
    PORTAL_AUTO_SYNC: bool = False  # set true when DISHA/Hero Biz APIs are configured
    PORTAL_SYNC_INTERVAL_MINUTES: int = 60

    # Security
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: str = "http://localhost:8080,http://localhost:5173,http://127.0.0.1:8080"

    # Business rules
    PROFIT_MARGIN_PCT: float = 0.22
    ESO_CAPACITY_ORDERS: int = 50
    STOCK_SHORTAGE_HORIZON_DAYS: int = 7
    SLA_ISSUANCE_HOURS: int = 24
    SLA_EMBOSSING_HOURS: int = 48
    SLA_DC_HOURS: int = 24
    SLA_DISPATCH_HOURS: int = 48
    SLA_FITMENT_HOURS: int = 72

    # Azure OpenAI
    AZURE_OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_API_VERSION: str = "2024-12-01-preview"
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = "gpt-4o"
    PAGEINDEX_MODEL: str | None = None
    OPENAI_API_VERSION: str | None = None

    # OEM portal integrations (configure for live sync)
    DISHA_API_URL: str | None = None
    DISHA_API_KEY: str | None = None
    HERO_BIZ_API_URL: str | None = None
    HERO_BIZ_API_KEY: str | None = None
    OLD_VEHICLE_PORTAL_API_URL: str | None = None
    OLD_VEHICLE_PORTAL_API_KEY: str | None = None
    POS_PORTAL_API_URL: str | None = None
    POS_PORTAL_API_KEY: str | None = None
    PORTAL_SYNC_TIMEOUT_SECONDS: int = 30

    model_config = SettingsConfigDict(
        env_file=[str(p) for p in _ENV_FILES if p.exists()],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("AUTO_SEED_DEMO", mode="before")
    @classmethod
    def default_auto_seed(cls, v, info):
        if v is not None and str(v).lower() not in ("", "none"):
            return str(v).lower() in ("1", "true", "yes")
        env = (info.data or {}).get("ENVIRONMENT", "development")
        return env == "development"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def default_debug(cls, v, info):
        if v is not None and str(v).lower() not in ("", "none"):
            return str(v).lower() in ("1", "true", "yes")
        env = (info.data or {}).get("ENVIRONMENT", "development")
        return env != "production"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def frontend_dist_path(self) -> Path:
        return Path(self.FRONTEND_DIST)

    @property
    def azure_api_version(self) -> str:
        return self.OPENAI_API_VERSION or self.AZURE_OPENAI_API_VERSION

    @property
    def azure_deployment(self) -> str:
        return self.PAGEINDEX_MODEL or self.AZURE_OPENAI_CHAT_DEPLOYMENT

    @property
    def azure_configured(self) -> bool:
        return bool(self.AZURE_OPENAI_API_KEY and self.AZURE_OPENAI_ENDPOINT and self.azure_deployment)

    @property
    def use_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


settings = Settings()

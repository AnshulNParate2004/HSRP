# Production Deployment — Real Industries HSRP Platform

## Overview

This platform is configured for **production** operation with:

- **PostgreSQL** database (recommended)
- **JWT authentication** and role-based access
- **Background jobs** (alerts every 15 min, OEM portal sync hourly)
- **WebSocket** live monitoring feed
- **OEM portal integrations** (DISHA, Hero Biz, Old Vehicle Portal, POS)
- **Executive PPT export**
- **Audit logging** for admin actions
- **No auto demo seed** in production

## Quick start (Docker)

```bash
# 1. Set secrets
cp backend/.env.example backend/.env
# Edit SECRET_KEY, BOOTSTRAP_ADMIN_PASSWORD, Azure OpenAI, portal API keys

# 2. Start stack
docker compose up -d --build

# 3. Sign in
# URL: http://localhost:8000/login
# Email: admin@realindustries.in (or BOOTSTRAP_ADMIN_EMAIL)
# Password: value from BOOTSTRAP_ADMIN_PASSWORD — change after first login
```

## Environment variables

| Variable | Production value |
|----------|----------------|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `AUTO_SEED_DEMO` | `false` |
| `DATABASE_URL` | `postgresql+psycopg2://user:pass@host:5432/hsrp_ops` |
| `SECRET_KEY` | Strong random 32+ bytes |
| `CORS_ORIGINS` | Your production frontend URL(s) |
| `SCHEDULER_ENABLED` | `true` |
| `DISHA_API_URL` / `DISHA_API_KEY` | Live portal credentials |
| `HERO_BIZ_API_URL` / `HERO_BIZ_API_KEY` | Live portal credentials |

## Roles

| Role | Access |
|------|--------|
| `admin` | Full platform + user management + audit logs |
| `executive` | All analytics, PPT export |
| `operations_manager` | Analytics + portal sync + alert generation |
| `state_manager` | Scoped to assigned states (set `allowed_state_ids`) |
| `viewer` | Read-only analytics |

## OEM portal sync

Configure REST endpoints that return JSON orders:

```json
[
  {
    "external_id": "DISHA-12345",
    "order_number": "RM-2026-001234",
    "vehicle_type": "new",
    "oem_name": "Maruti Suzuki",
    "state_code": "MH",
    "revenue": 450,
    "current_stage": "embossing_pending",
    "order_date": "2026-05-30T10:00:00Z"
  }
]
```

Trigger manually: `POST /api/v1/integrations/sync` (requires ops_manager+).

## WebSocket monitoring

Connect: `ws://host/api/v1/ws/monitoring?token=<JWT>`

Receives `live_summary` payload every 10 seconds.

## Development vs production

| | Development | Production |
|--|-------------|------------|
| Database | SQLite OK | PostgreSQL |
| Demo seed | `AUTO_SEED_DEMO=true` | `false` |
| API docs | `/docs` enabled | Disabled |
| Login | Bootstrap admin auto-created | Change default password |

## Create additional users

```bash
curl -X POST http://localhost:8000/api/v1/auth/users \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ops.mh@realindustries.in",
    "password": "SecurePass123!",
    "full_name": "MH Operations",
    "role": "state_manager",
    "allowed_state_ids": [1]
  }'
```

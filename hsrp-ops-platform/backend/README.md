# Real Mazon HSRP Ops — Backend (FastAPI + SQLite)

Python API for HSRP operations analytics. Can also **serve the Vite frontend build** from port 8000.

## Run both (from project root)

```bash
cd hsrp-ops-platform
npm install
npm run install:all
npm run dev
```

- Frontend: http://localhost:8080
- API: http://localhost:8000/docs

Or double-click **`start-dev.bat`** in the project root.

## Quick start (backend only)

```bash
cd backend
pip install -r requirements.txt

# Optional: reset demo data
python -m app.db.seed

# Run API (+ Vite frontend if frontend/dist exists)
python -m uvicorn app.main:app --reload --port 8000
```

Open:
- **App (Vite build):** http://localhost:8000/app
- **API docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

## Serve Vite frontend from backend

Build the frontend first, then start the backend:

```bash
cd ../frontend
npm install
npm run build

cd ../backend
python -m uvicorn app.main:app --port 8000
```

The backend serves `frontend/dist` automatically when it exists.

Set `SERVE_FRONTEND=false` in `.env` to disable static serving (API only).

## Development (two terminals)

| Terminal | Command | URL |
|----------|---------|-----|
| Backend | `uvicorn app.main:app --reload --port 8000` | API |
| Frontend | `npm run dev` (in `frontend/`) | http://localhost:8080 |

Vite dev server proxies `/api` → backend :8000.

## API routes

All analytics under `/api/v1/`:

- `GET /api/v1/dashboard/summary`
- `GET /api/v1/revenue/by-state`
- `GET /api/v1/pendency/by-stage`
- `GET /api/v1/performance/eso`
- `GET /api/v1/inventory/overview`
- `GET /api/v1/tat/by-stage`
- `GET /api/v1/alerts`
- `POST /api/v1/alerts/generate`

## Database

SQLite file: `backend/hsrp_ops.db`

Auto-seeds demo data on first startup if the database is empty.

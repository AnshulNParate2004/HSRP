# HSRP Ops Platform — Backend (FastAPI + SQLite)

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

Default dev login: `admin@hsrp-ops.local` / `Admin@123`. If you previously seeded with another admin email, delete `hsrp_ops.db` and restart to pick up the new bootstrap credentials.

## Deploy to Hugging Face (Docker Space)

Use this backend with the Vercel frontend (`VITE_API_URL` → your HF Space URL).

### 1. Create a Docker Space

1. [huggingface.co/spaces](https://huggingface.co/spaces) → **Create new Space**
2. SDK: **Docker**
3. Name e.g. `hsrp-api` → URL: `https://Anshul2004-hsrp-api.hf.space`

### 2. Push this folder to the Space

Clone the Space repo, copy these files into its root, then push:

```
app/
requirements.txt
Dockerfile
README.HF.md  → rename to README.md on the Space repo
```

```bash
git clone https://huggingface.co/spaces/Anshul2004/hsrp-api
cd hsrp-api

# From your machine (PowerShell example)
Copy-Item -Recurse ..\HSRP\hsrp-ops-platform\backend\app .
Copy-Item ..\HSRP\hsrp-ops-platform\backend\requirements.txt .
Copy-Item ..\HSRP\hsrp-ops-platform\backend\Dockerfile .
Copy-Item ..\HSRP\hsrp-ops-platform\backend\README.HF.md README.md

git add .
git commit -m "Deploy HSRP FastAPI backend"
git push
```

### 3. Space secrets (Settings → Variables and secrets)

| Variable | Value |
|----------|--------|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `SERVE_FRONTEND` | `false` |
| `SECRET_KEY` | Generate: `openssl rand -hex 32` |
| `CORS_ORIGINS` | Your Vercel URL, e.g. `https://your-app.vercel.app` |
| `AUTO_SEED_DEMO` | `true` (demo data) |
| `BOOTSTRAP_ADMIN_EMAIL` | `admin@hsrp-ops.local` |
| `BOOTSTRAP_ADMIN_PASSWORD` | Strong password |

### 4. Verify & connect Vercel

- Health: `https://Anshul2004-hsrp-api.hf.space/health`
- Vercel env: `VITE_API_URL=https://Anshul2004-hsrp-api.hf.space/api/v1` then redeploy

**Note:** SQLite on HF is ephemeral (resets on redeploy). For persistent production data, use PostgreSQL (`DATABASE_URL`) on Neon/Supabase.

# Real Mazon — HSRP Operations Platform

Full-stack app: **FastAPI + SQLite** backend, **Vite + React** frontend.

## One-command setup

```powershell
cd d:\Internship\HSBC\hsrp-ops-platform
npm install
npm run install:all
npm run seed
```

## Run both (development)

```powershell
npm run dev
```

| Service  | URL |
|----------|-----|
| **Frontend (Vite)** | http://localhost:8080 |
| **Backend API**     | http://localhost:8000 |
| **API docs**        | http://localhost:8000/docs |

Vite proxies `/api` → backend on port 8000.

## Run both (production-style, single port)

```powershell
npm run start
```

Builds frontend, then serves everything from **http://localhost:8000**

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Backend + Vite dev server together |
| `npm run dev:backend` | FastAPI only (:8000) |
| `npm run dev:frontend` | Vite only (:8080) |
| `npm run build` | Build Vite frontend → `frontend/dist` |
| `npm run start` | Build + serve app from backend :8000 |
| `npm run seed` | Reset SQLite demo data |
| `npm run install:all` | Install Python + Node deps |

## Windows shortcuts

- **`start-dev.bat`** — run backend + frontend (dev)
- **`backend/run.bat`** — backend only

## Project layout

```
hsrp-ops-platform/
├── package.json       ← run both from here
├── backend/           ← FastAPI + SQLite
│   ├── app/
│   └── hsrp_ops.db
└── frontend/          ← Vite + React
    ├── src/
    └── dist/          ← production build
```

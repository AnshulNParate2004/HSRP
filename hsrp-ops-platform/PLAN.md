# HSRP Operations & Analytics Platform — Implementation Plan

**Client:** Real Industries Limited (Real Mazon — The Vehicle Identification Company)  
**Reference UI:** [revenue-navigator](D:\Internship\Renewal-Upsell-Advisor\revenue-navigator)  
**Stack:** Vite + React + TypeScript + Tailwind + shadcn/ui (frontend) · FastAPI + SQLite (backend, Phase 1)

---

## 1. Vision

Centralized, real-time visibility into the full HSRP lifecycle: **order receipt → issuance → embossing → dispatch → inventory → fitment → performance monitoring** across India, with AI-driven alerts and predictive intelligence.

---

## 2. Module Map (from AI Framework document)

| # | Module | Backend Service | Frontend Page |
|---|--------|-----------------|---------------|
| 1 | OEM Contribution & Revenue Analytics | `revenue_analytics` | `/app/revenue` |
| 2 | Pendency & Delay Monitoring | `pendency_monitor` | `/app/pendency` |
| 3 | Operational Performance Analytics | `performance_analytics` | `/app/performance` |
| 4 | Stock Inventory & Consumption | `inventory_intelligence` | `/app/inventory` |
| 5 | AI Smart Alerts & Predictions | `ai_alerts` | `/app/alerts` + dashboard panel |
| 6 | Real-Time Dashboard | aggregation of all services | `/app` (home) |
| 7 | TAT Analysis | `tat_analysis` | `/app/tat` |
| 8 | Predictive Inventory Planning | `inventory_intelligence` | `/app/inventory/planning` |

---

## 3. Data Model (SQLite Phase 1)

```
states ──┬── esos
         ├── dealers
         ├── warehouses
         └── orders

oems ────┬── orders
         └── inventory

portals ── orders

orders ──┬── order_stage_history (TAT)
         └── rejections

inventory ── inventory_consumption

alerts (AI-generated)
```

### Order lifecycle stages
`received → issuance → embossing → dc → dispatch → fitment → completed`

### Vehicle types
`new` | `old`

### Source portals
DISHA · Hero Biz · Old Vehicle Portal · POS

---

## 4. Backend Architecture

```
backend/
  app/
    main.py                 # FastAPI entry, CORS, lifespan
    core/config.py          # Settings (SQLite path, API prefix)
    db/
      session.py            # SQLAlchemy engine + SessionLocal
      seed.py               # Demo PAN-India sample data
    models/                 # SQLAlchemy ORM
    schemas/                # Pydantic response models
    services/
      revenue_analytics.py  # State/OEM/portal revenue, trends
      pendency_monitor.py   # Stage bottlenecks, delay detection
      performance_analytics.py  # ESO productivity, rejections
      inventory_intelligence.py # Stock levels, shortage prediction
      tat_analysis.py       # Stage-wise turnaround times
      ai_alerts.py          # Rule engine + simple forecasting
    api/v1/
      api.py                # Router aggregation
      endpoints/            # Thin controllers → services
```

### API prefix: `/api/v1`

| Endpoint group | Key routes |
|----------------|------------|
| Dashboard | `GET /dashboard/summary` |
| Revenue | `GET /revenue/overview`, `/revenue/by-state`, `/revenue/by-oem`, `/revenue/trends` |
| Pendency | `GET /pendency/overview`, `/pendency/by-stage`, `/pendency/critical` |
| Performance | `GET /performance/eso`, `/performance/rejections` |
| Inventory | `GET /inventory/overview`, `/inventory/shortage-risk` |
| TAT | `GET /tat/overview`, `/tat/by-stage` |
| Alerts | `GET /alerts`, `POST /alerts/generate` |
| Orders | `GET /orders`, `GET /orders/{id}` |

---

## 5. AI / Intelligence Logic (Phase 1 — Rule Engine)

Phase 1 uses **deterministic rules + moving averages** (no ML deps). Phase 2 can add scikit-learn / Prophet.

| Alert Type | Rule |
|------------|------|
| Stock shortage (7-day) | `avg_daily_consumption × 7 > current_stock` |
| Underperforming ESO | completion rate < 70% of state average |
| Dispatch delay | orders in `dispatch` stage > SLA (48h) |
| Rejection spike | rejections this week > 2× 4-week average |
| Revenue drop | state revenue this month < 85% of 3-month avg |
| Pendency critical | stage pending > SLA threshold |

---

## 6. Frontend Plan (revenue-navigator style)

**Copy patterns from revenue-navigator:**
- Vite + React 18 + TypeScript + Tailwind + shadcn/ui
- `AppLayout` with collapsible sidebar + TopBar
- DM Sans / Plus Jakarta Sans fonts, indigo primary, black 2px borders on cards
- TanStack Query for API calls, Recharts for charts, Framer Motion for cards
- Proxy `/api` → `localhost:8000`

### Pages & navigation
```
Dashboard          → KPI cards + live orders + AI alert digest
Revenue Analytics  → State/OEM charts, portal breakdown, export
Pendency Monitor   → Stage funnel, delay heatmap, ESO drill-down
Performance        → ESO leaderboard, rejection trends
Inventory          → Stock by state/OEM/size/color, replenishment
TAT Analysis       → Stage-wise benchmarks, delay root cause
Alerts             → Exception list, severity filters
Reports            → CSV/PPT export (Phase 2)
Settings           → SLA thresholds, portal config
```

### Branding
- Logo: Real Mazon / Real Industries
- Accent: transport/security theme (deep blue + orange accent)

---

## 7. Implementation Phases

### Phase 1 — Foundation (current)
- [x] SQLite schema + seed data
- [x] Analytics services + REST API
- [x] Frontend scaffold (revenue-navigator style)
- [x] Dashboard + Revenue + Pendency + Performance + Inventory + TAT + Alerts pages

### Phase 2 — Intelligence
- ML forecasting (order volume, festival demand)
- Geo heatmaps (India state map)
- Report export (CSV, PPT)
- Auth (JWT / role-based: executive, ops, state manager)

### Phase 3 — Integrations
- OEM portal connectors (DISHA, Hero Biz)
- ESO / embossing station real-time feeds
- WebSocket live dashboard
- PostgreSQL migration for production

---

## 8. How to Run

### Both backend + frontend (recommended)

```bash
cd hsrp-ops-platform
npm install && npm run install:all
npm run dev
```

| Service | URL |
|---------|-----|
| Frontend (Vite) | http://localhost:8080 |
| Backend API | http://localhost:8000/docs |

Or double-click **`start-dev.bat`**.

### Backend only

```bash
cd hsrp-ops-platform/backend
pip install -r requirements.txt
python -m app.db.seed        # load sample data
uvicorn app.main:app --reload --port 8000
```

### Production (single port)

```bash
cd hsrp-ops-platform
npm run start                # builds frontend, serves from :8000
```

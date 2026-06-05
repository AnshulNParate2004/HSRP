# Real Mazon HSRP Ops — Frontend (Vite + React)

Vite + React 18 + TypeScript + Tailwind CSS dashboard for HSRP operations analytics.

Same stack as [revenue-navigator](https://github.com): Vite, shadcn-style UI, TanStack Query, Recharts, Framer Motion.

## Prerequisites

- Node.js 18+
- Backend API running on port **8000**

## Quick start

```bash
# 1. Start backend (separate terminal)
cd ../backend
python -m uvicorn app.main:app --port 8000

# 2. Start Vite dev server
cd ../frontend
npm install
npm run dev
```

Open **http://localhost:8080**

## Vite scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Vite dev server (port 8080, HMR) |
| `npm run build` | TypeScript check + production build → `dist/` |
| `npm run preview` | Preview production build locally |

## Project structure

```
frontend/
├── index.html          # Vite entry HTML
├── vite.config.ts      # Vite config + API proxy
├── tailwind.config.ts
├── src/
│   ├── main.tsx        # React bootstrap
│   ├── App.tsx         # Routes
│   ├── pages/          # Dashboard pages
│   ├── components/     # Layout + charts
│   └── lib/api/        # Backend API client
└── dist/               # Build output (after npm run build)
```

## API proxy

In dev, Vite proxies `/api/*` → `http://127.0.0.1:8000` (see `vite.config.ts`).

For production, set `VITE_API_URL` to your backend URL.

---
title: HSRP Ops API
emoji: 🚗
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# HSRP Operations & Analytics API

FastAPI backend for the HSRP Ops platform. Pairs with the Vite frontend on Vercel.

## Endpoints

| URL | Description |
|-----|-------------|
| `/health` | Health check |
| `/api` | API info |
| `/api/v1/...` | Analytics & auth routes |

## Required secrets (Space Settings)

| Variable | Example |
|----------|---------|
| `SECRET_KEY` | `openssl rand -hex 32` |
| `CORS_ORIGINS` | `https://your-app.vercel.app` |
| `BOOTSTRAP_ADMIN_PASSWORD` | Strong password |

## Vercel frontend

Set on Vercel:

```
VITE_API_URL=https://Anshul2004-hsrp-api.hf.space/api/v1
```

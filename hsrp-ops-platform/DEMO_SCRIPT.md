# Real Mazon HSRP Ops — Demo Presenter Script

**Company:** Real Industries Limited  
**Platform:** Real Mazon — HSRP Operations & Analytics  
**Duration:** 25–35 minutes (full) | 12–15 minutes (short)  
**Login:** `admin@realindustries.in` / `Admin@123`  
**Start app:** `npm run dev` or `npm run start` → open `http://localhost:8000`

---

## Before You Start (30 seconds)

> "Today I'll show Real Mazon — our AI-powered HSRP operations platform. It gives Real Industries a single pane of glass across the full HSRP lifecycle: orders, revenue, pendency, inventory, TAT, live monitoring, AI alerts, and an AI assistant — all PAN India, for both new and old vehicle programs."

**Pre-check:**
- Backend running on port 8000
- Frontend loaded
- Demo data seeded (orders, states, ESOs visible)

---

## 1. Landing Page (`/`)

**Navigate:** Open `http://localhost:8000`

**Say:**
> "This is the public entry point for Real Mazon. The platform is built for Real Industries Limited — our national HSRP operations arm."

**Point out:**
- Logo & brand — Real Mazon / HSRP Ops
- Headline — "AI-Powered HSRP Operations & Analytics"
- Four capability cards:
  - Revenue Analytics
  - Pendency Monitor
  - Inventory Intelligence
  - AI Assistant

**Say:**
> "From here, authorized users sign in to the operations dashboard. Everything behind login is role-protected and audit-logged."

**Action:** Click **"Launch Operations Dashboard"** or **"Sign in"**

---

## 2. Login (`/login`)

**Say:**
> "Access is secured with JWT authentication. Each user has a role — admin, executive, operations manager, state manager, or viewer — which controls what they can sync, export, or configure."

**Action:** Enter credentials and click **Sign in**

**Say:**
> "On first deployment, the system bootstraps an admin account. In production, passwords and secrets are set via environment configuration — not hardcoded."

---

## 3. App Shell — Layout Every Screen Shares

Once logged in, explain the frame before diving into pages.

### Left Sidebar

**Say:**
> "The sidebar is the main navigation. It's driven by platform configuration from the backend — so we can add or reorder modules without redeploying the frontend."

**Point out:**
- Real Mazon branding
- PAN India monitoring green pulse at bottom
- Sidebar can collapse (click top bar)

### Top Bar (Global Controls)

**Say:**
> "Across every screen, these global controls apply."

| Control | What to say |
|--------|-------------|
| Vehicle filter (All / New / Old) | "HSRP runs two programs — new vehicle and old vehicle. This filter applies to every analytics view instantly." |
| AI badge (if shown) | "When Azure OpenAI is configured, you'll see the active model here — e.g. GPT-4o." |
| Bell icon | "Quick jump to AI Alerts." |
| User name + Logout | "Session ends here; all API calls require a valid token." |

**Demo tip:** Toggle **New Vehicle** → **Old Vehicle** → **All Vehicles** on the Dashboard to show live data refresh.

---

## 4. Dashboard (`/app`) — 4 minutes

**Say:**
> "This is the command center — a single snapshot of national HSRP health."

### Metric cards (top row)

Walk through each card:

> "**Total Orders** — national order volume.  
> **Total Revenue** — rupee contribution across states and OEMs.  
> **Pending Orders** — work still in the pipeline.  
> **Completed** — successfully closed orders.  
> **Critical Alerts** — AI-flagged exceptions needing action.  
> **Avg TAT** — average turnaround in hours.  
> **New / Old Vehicle** — split by program.  
> **Active ESOs / OEMs** — how many embossing stations and OEMs are live."

### PAN India State Heatmap

**Say:**
> "This geo heatmap shows active orders by state. Darker/warmer states mean higher workload. Leadership can spot regional bottlenecks in seconds — Maharashtra, Karnataka, Tamil Nadu, etc."

**Action:** Hover a state — show tooltip with state name and order count.

### Weekly Order & Revenue Trends

**Say:**
> "This line chart tracks weekly order volume and revenue together — so we see whether growth is volume-driven or value-driven."

### AI Alert Digest (right panel)

**Say:**
> "Top 5 alerts surface here automatically. The system runs a background job every 15 minutes to detect SLA breaches, stock risks, and performance issues."

**Action:** Click **"View all"** → briefly show Alerts page → come back to Dashboard.

### Live Orders table

**Say:**
> "This is the operational pulse — real orders with state, OEM, current stage, vehicle type, revenue, and hours stuck in the current stage."

**Explain stages:**
> "An order moves: Received → Issuance → Embossing → DC → Dispatch → Fitment → Completed. Hours in stage tells us where delays start."

---

## 5. Live Monitor (`/app/monitoring`) — 3 minutes

**Say:**
> "Dashboard is summary; Live Monitor is the control room. Data refreshes every 30 seconds."

### Live metric tiles

> "**Active Orders** — orders in flight right now.  
> **New / Old Vehicle Live** — split by program.  
> **In Embossing / Dispatch / Fitment** — stage-specific live counts."

### State heatmap

**Say:**
> "Same geo view, but focused on *active* orders only — what's happening right now, not historical."

### Embossing & Dispatch monitors

**Say:**
> "Embossing shows orders in embossing, how many are delayed, and average wait time. Dispatch shows in-transit volume and delayed dispatches."

### ESO Workload table

**Say:**
> "Every Embossing Service Operator's load is visible — pending orders, load percentage, and status. If an ESO is overloaded, we redistribute work before SLAs break."

### Dealer & Fitment Center Activity

**Say:**
> "Downstream visibility — which dealers and fitment centers are active, order counts, and revenue contribution."

---

## 6. Revenue (`/app/revenue`) — 3 minutes

**Say:**
> "Revenue Analytics answers: where is money coming from, and where should we invest capacity?"

| Chart | Script |
|-------|--------|
| Revenue by State | "Top 10 states by revenue and order count." |
| Revenue by OEM | "Hero, Honda, TVS, Bajaj — OEM-wise contribution." |
| Portal Contribution | "Pie chart — DISHA, Hero Biz, Old Vehicle Portal, POS — which channel feeds orders." |
| Order Volume Trend | "Weekly order trend." |
| Dealer & Fitment Centers | "Which dealers drive revenue." |
| State Profitability | "Estimated profit at ~22% margin — configurable in backend." |
| OEM Comparison (New vs Old) | "Side-by-side new vs old vehicle revenue per OEM." |

**Demo tip:** Switch to **New Vehicle** filter and say:
> "Notice how every chart recalculates — same platform, filtered context."

---

## 7. Pendency (`/app/pendency`) — 2 minutes

**Say:**
> "Pendency is where operations lives day-to-day — what's stuck and for how long."

### KPI row

> "**Total Pending**, **Delayed**, and **Delay Rate %** — national pendency health."

### Pending by Stage

**Say:**
> "Bar chart shows pending vs delayed per stage. If embossing has high delayed count, that's our bottleneck."

### Pending by State

**Say:**
> "Which states are holding the most pending orders."

### Critical SLA Breaches table

**Say:**
> "These orders have exceeded SLA thresholds — order number, stage, overdue hours, vehicle type. This is the escalation list for ops managers."

---

## 8. Performance (`/app/performance`) — 2 minutes

**Say:**
> "Performance tracks ESO productivity and quality."

### ESO Completion Rate (Bottom 10)

**Say:**
> "We surface the bottom 10 ESOs by completion rate — early warning before customer complaints."

### Rejection Trends

**Say:**
> "Weekly rejection trend — quality issues over time."

### ESO Leaderboard table

**Say:**
> "Full leaderboard: orders, completed, completion %, rejections, avg TAT. Green above 80%, amber below."

### State Operational Activity

**Say:**
> "Total vs completed orders by state — operational throughput."

---

## 9. Inventory (`/app/inventory`) — 2 minutes

**Say:**
> "Plate stock is as critical as order flow. This module prevents embossing stops due to blank plate shortages."

### KPI row

> "**Total SKUs**, **Low/Critical Stock**, **Shortage Risks (7 days)**."

### Stock by Size & Color

**Say:**
> "Breakdown by plate size and color — HSRP has multiple SKU dimensions."

### 7-Day Shortage Risk

**Say:**
> "AI predicts which state-OEM combinations will run out in 7 days, with a replenishment recommendation."

### Top Stock by State

**Say:**
> "Where inventory is concentrated nationally."

---

## 10. Planning (`/app/planning`) — 2 minutes

**Say:**
> "Planning moves from reactive to predictive — forecast demand and plan procurement."

### KPI row

> "**Min Stock Alerts**, **Procurement Items**, **Inter-state Transfers**."

### Order & Revenue Forecast

**Say:**
> "Historical actuals plus forward forecast — blue is history, orange is projected."

### Festival Demand Forecast

**Say:**
> "India-specific — festival months drive HSRP spikes. We project order volume by month."

### Automated Replenishment Plan

**Say:**
> "System recommends how many units to order per state-OEM-SKU, with priority badges."

### Inter-State Stock Balancing

**Say:**
> "If Gujarat has surplus and Rajasthan is short, the system suggests transfers with reasoning."

---

## 11. TAT Analysis (`/app/tat`) — 2 minutes

**Say:**
> "TAT — Turnaround Time — is our SLA backbone."

### Average TAT by Stage

**Say:**
> "Average and P90 hours per lifecycle stage. P90 catches outliers that averages hide."

### Stage-wise detail table

**Say:**
> "Full breakdown with sample counts — statistically meaningful only where we have enough data."

### Total TAT by State

**Say:**
> "End-to-end TAT for completed orders — which states close fastest."

---

## 12. AI Alerts (`/app/alerts`) — 2 minutes

**Say:**
> "Alerts are the exception engine — the system watches so managers don't have to."

### Severity counts

> "Critical, High, Medium, Low — at a glance."

### Alert cards

**Say for each type:**
> "Each alert has a type, severity, title, message, and an AI **recommendation** — not just 'something is wrong', but what to do next."

**Action:** Click **Regenerate**

**Say:**
> "Regenerate re-runs the AI alert engine on live data — useful after a sync or major operational change."

---

## 13. AI Assistant (`/app/assistant`) — 3 minutes

**Say:**
> "This is the conversational layer. Ask questions in plain English; the assistant queries live data using LangChain tools."

**Point out:**
- Context badge shows current vehicle filter
- Quick Prompts on the right (auto-generated from live data)

### Demo questions (pick 2–3)

1. **"What is our total revenue across all orders?"**  
   > "Pulls live revenue from the database."

2. **"Which state has the highest revenue?"**  
   > "Runs state-wise revenue analytics."

3. **"Show critical pendency and SLA breaches"**  
   > "Surfaces pendency intelligence."

4. **"Any stock shortage risks in the next 7 days?"**  
   > "Checks inventory intelligence."

5. **"Which ESOs are underperforming?"**  
   > "Queries ESO performance data."

**Say after answer:**
> "Notice the footer — it shows whether Azure OpenAI answered, or the rule engine fallback, and which data tools were used."

**If Azure not configured:**
> "Without Azure OpenAI keys, the assistant still works via rule-based intelligence. With Azure configured, answers are richer and more conversational."

**Action:** Click **Clear chat** when done.

---

## 14. Reports (`/app/reports`) — 2 minutes

**Say:**
> "Management doesn't live in dashboards — they need exports. This is the MIS layer."

### Executive Management Summary

**Say:**
> "Auto-generated narrative summary with KPIs and AI recommendations — ready for a Monday morning review."

### Download PPT

**Action:** Click **Download PPT**

**Say:**
> "One-click executive PowerPoint — KPIs, alerts, top states. For board meetings and OEM reviews."

### CSV exports (5 reports)

| Report | Say |
|--------|-----|
| Revenue Analytics CSV | "State, OEM, portal breakdown." |
| Pendency MIS CSV | "Stage bottlenecks and SLA breaches." |
| Performance Report CSV | "ESO productivity and rejections." |
| Inventory Report CSV | "Stock levels and shortage risk." |
| TAT Analysis CSV | "Lifecycle turnaround benchmarks." |

### Priority Alerts section

**Say:**
> "Critical alerts embedded in the management report pack."

---

## 15. Integrations (`/app/integrations`) — 3 minutes

*This is the configuration screen in the UI.*

**Say:**
> "There is no separate Settings page — operational configuration lives here and in the backend environment file. This is where we connect live OEM portals."

### Portal status cards (4 portals)

> "**DISHA**, **Hero Biz**, **Old Vehicle Portal**, and **POS** — each shows configured or not configured."

### Yellow info banner

**Say:**
> "In demo mode, portal APIs aren't configured yet — so sync shows 'Skipped'. In production, we add API URLs and keys to `backend/.env` and enable `PORTAL_AUTO_SYNC=true` for hourly automatic sync."

**Action (if admin):** Click **Sync now**

**Say:**
> "Manual sync pulls orders from all configured portals and upserts into our database. Results show fetched and upserted counts."

### Sync history table

**Say:**
> "Full audit trail — portal, status, records fetched, records upserted, timestamp."

**Admin only:** Mention **Clear old skipped logs** — housekeeping for demo environments.

---

## 16. Backend Configuration (Technical Audience)

**Say:**
> "Platform settings are environment-driven for security. Key configuration in `backend/.env`:"

| Setting | Purpose |
|---------|---------|
| `DATABASE_URL` | PostgreSQL in production |
| `SECRET_KEY` | JWT signing |
| `BOOTSTRAP_ADMIN_*` | First admin account |
| `CORS_ORIGINS` | Allowed frontend domains |
| `AZURE_OPENAI_*` | AI Assistant + richer alerts |
| `DISHA_API_URL`, `HERO_BIZ_API_URL`, etc. | Live portal sync |
| `PORTAL_AUTO_SYNC` | Hourly automatic sync |
| `PROFIT_MARGIN_PCT` | Revenue profitability (shown on Revenue page) |
| `SCHEDULER_ENABLED` | Background alert jobs |
| `ALERT_JOB_INTERVAL_MINUTES` | How often alerts regenerate |

**Say:**
> "Admin-only API endpoints exist for user management and audit logs — exposed via REST for future admin UI."

---

## Closing (1 minute)

**Say:**
> "To summarize: Real Mazon gives Real Industries end-to-end HSRP visibility — from national dashboard to state-level heatmaps, from revenue and pendency to inventory planning and TAT, with AI alerts and a conversational assistant, plus one-click MIS exports and live OEM portal integration."

> "It replaces spreadsheet MIS, disconnected portal logins, and reactive firefighting — with one AI-powered operations platform across PAN India."

**End on Dashboard** with **All Vehicles** selected.

---

## Short Demo Path (12 minutes)

1. Landing → Login (1 min)
2. Dashboard + vehicle filter + heatmap (3 min)
3. Live Monitor (2 min)
4. Pendency → SLA breaches (2 min)
5. AI Assistant — 1 question (2 min)
6. Reports — download PPT (1 min)
7. Integrations — portal config (1 min)

---

## Demo Tips

- Always show the **vehicle filter** at least once — it's a key differentiator.
- **Hover the heatmap** — visual impact is high.
- On **Alerts**, click **Regenerate** live.
- On **Assistant**, use a **Quick Prompt** button — faster than typing.
- If asked about mobile: sidebar collapses; mobile nav exists on smaller screens.
- Default login is shown on the login page for demo convenience.

---

## HSRP Order Lifecycle Reference

| Stage | Label |
|-------|-------|
| 1 | Received |
| 2 | Issuance Pending |
| 3 | Embossing Pending |
| 4 | DC Pending |
| 5 | Dispatch Pending |
| 6 | Fitment Pending |
| 7 | Completed |

---

## Navigation Map

| Sidebar Item | Route |
|--------------|-------|
| Dashboard | `/app` |
| Live Monitor | `/app/monitoring` |
| Revenue | `/app/revenue` |
| Pendency | `/app/pendency` |
| Performance | `/app/performance` |
| Inventory | `/app/inventory` |
| Planning | `/app/planning` |
| TAT Analysis | `/app/tat` |
| AI Alerts | `/app/alerts` |
| AI Assistant | `/app/assistant` |
| Reports | `/app/reports` |
| Integrations | `/app/integrations` |

---

*Real Mazon HSRP Operations Platform — Real Industries Limited*

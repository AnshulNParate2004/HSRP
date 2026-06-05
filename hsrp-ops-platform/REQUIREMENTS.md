# AI Framework Document — Feature Coverage

Mapping of **AI Framework-Real Industries Ltd..docx** requirements to the platform.

## 1. OEM Contribution & Revenue Analytics

| Requirement | Status | Location |
|-------------|--------|----------|
| State-wise revenue & order count | ✅ | `/app/revenue` |
| OEM-wise revenue & order count | ✅ | `/app/revenue` |
| State-wise OEM contribution | ✅ | API `/revenue/state-oem-matrix` |
| Daily / weekly / monthly trends | ✅ | API `granularity=day\|week\|month` |
| Portal analytics (DISHA, Hero Biz, etc.) | ✅ | `/app/revenue` pie chart |
| New & Old vehicle analytics | ✅ | TopBar filter (All/New/Old) |
| Dealer & fitment contribution | ✅ | `/app/revenue` dealer chart |
| State profitability analysis | ✅ | `/app/revenue` profitability chart |
| OEM comparative analysis | ✅ | `/app/revenue` new vs old OEM |
| Revenue trend forecasting | ✅ | `/app/planning` |
| Downloadable reports | ✅ | `/app/reports` CSV export |
| PPT export | ⏳ Phase 2 | Requires python-pptx |

## 2. Pendency & Delay Monitoring

| Requirement | Status | Location |
|-------------|--------|----------|
| State / OEM / ESO pendency | ✅ | `/app/pendency` |
| Stage bottlenecks (Issuance, Embossing, DC, Fitment) | ✅ | `/app/pendency` |
| Date-wise ESO delay | ✅ | API `/pendency/eso-delay-by-date` |
| Monthly stage overview | ✅ | API `/pendency/monthly-overview` |
| Critical SLA escalation | ✅ | `/app/pendency` + `/app/alerts` |
| New & Old vehicle dashboards | ✅ | Vehicle filter |
| Downloadable MIS | ✅ | `/app/reports` pendency CSV |
| AI bottleneck detection | ✅ | AI Alerts rule engine |

## 3. Operational Performance Analytics

| Requirement | Status | Location |
|-------------|--------|----------|
| ESO performance & rejection analytics | ✅ | `/app/performance` |
| Monthly ESO overview | ✅ | API `/performance/monthly-eso` |
| State order frequency | ✅ | `/app/performance` |
| OEM order trends | ✅ | API `/performance/oem-trends` |
| Dealer order frequency | ✅ | API `/performance/dealer-frequency` |
| PAN India active OEM/Dealer/ESO counts | ✅ | Dashboard KPIs |
| Underperforming ESO detection | ✅ | AI Alerts + Assistant |
| Workload prediction | ✅ | `/app/monitoring` + `/app/planning` |
| Downloadable performance reports | ✅ | `/app/reports` |
| Management summaries | ✅ | `/app/reports` executive summary |

## 4. Stock Inventory & Consumption Analytics

| Requirement | Status | Location |
|-------------|--------|----------|
| Real-time inventory monitoring | ✅ | `/app/inventory` |
| OEM / state / size / color tracking | ✅ | `/app/inventory` |
| Warehouse visibility | ✅ | Inventory table |
| Shortage prediction (7-day) | ✅ | `/app/inventory` + AI Alerts |
| Festival demand forecasting | ✅ | `/app/planning` |
| Historical consumption | ✅ | API `/inventory/historical-consumption` |
| Inter-state stock balancing | ✅ | `/app/planning` |
| Replenishment alerts | ✅ | `/app/planning` procurement |
| Downloadable inventory reports | ✅ | `/app/reports` |

## 5. AI Smart Alerts & Predictive Intelligence

| Requirement | Status | Location |
|-------------|--------|----------|
| Stock shortage (7-day) | ✅ | `/app/alerts` |
| Underperforming ESOs | ✅ | `/app/alerts` |
| Monthly order volume forecast | ✅ | `/app/planning` |
| Dispatch delay prediction | ✅ | `/app/monitoring` dispatch monitor |
| Rejection spike detection | ✅ | `/app/alerts` |
| Corrective action recommendations | ✅ | Alert cards + Reports |
| Rule engine + trend forecasting | ✅ | Backend services |

## 6. Real-Time Dashboard & Monitoring

| Requirement | Status | Location |
|-------------|--------|----------|
| Live New & Old vehicle monitoring | ✅ | `/app/monitoring` |
| State-wise live tracking | ✅ | `/app/monitoring` heatmap |
| ESO workload visibility | ✅ | `/app/monitoring` |
| Embossing station monitoring | ✅ | `/app/monitoring` |
| Dispatch monitoring | ✅ | `/app/monitoring` |
| Dealer / fitment activity | ✅ | `/app/monitoring` |
| Interactive visual analytics | ✅ | All pages (Recharts) |
| Geo-based heatmaps | ✅ | Dashboard + Monitoring |
| Executive dashboard | ✅ | `/app` + `/app/reports` |
| Mobile & web accessibility | ✅ | Responsive layout |

## 7. TAT Analysis

| Requirement | Status | Location |
|-------------|--------|----------|
| Order → Issuance → Embossing → Dispatch → Fitment TAT | ✅ | `/app/tat` |
| State / OEM / ESO average TAT | ✅ | `/app/tat` + API |
| Delay trend analysis | ✅ | API `/tat/delay-trends` |
| Optimization recommendations | ✅ | API `/tat/recommendations` |
| Predictive TAT | ✅ | Trend-based via planning |

## 8. Predictive Inventory Planning

| Requirement | Status | Location |
|-------------|--------|----------|
| Minimum stock alerts | ✅ | `/app/planning` |
| Festival demand forecasting | ✅ | `/app/planning` |
| State-wise inventory prediction | ✅ | Shortage risk API |
| OEM-specific planning | ✅ | Procurement plan |
| Automated replenishment | ✅ | `/app/planning` |

## 9. AI Question & Answer Assistant

| Requirement | Status | Location |
|-------------|--------|----------|
| Ask questions, get answers from data | ✅ | `/app/assistant` |
| Revenue / pendency / stock / ESO / TAT queries | ✅ | LangChain + Azure OpenAI |

## Production capabilities (v1.0)

| Capability | Status | Location |
|------------|--------|----------|
| JWT auth & RBAC | ✅ | `/login`, `/api/v1/auth/*` |
| PostgreSQL + Docker | ✅ | `docker-compose.yml`, `PRODUCTION.md` |
| Background alert & portal sync jobs | ✅ | APScheduler |
| WebSocket live monitoring | ✅ | `/api/v1/ws/monitoring` |
| OEM portal HTTP integrations | ✅ | `/app/integrations`, env API keys |
| Executive PPT export | ✅ | `/app/reports` |
| Audit logs (admin) | ✅ | `/api/v1/admin/audit-logs` |
| Audit trail on login | ✅ | `audit_logs` table |

## Phase 2 (Future)

- Full India SVG map
- Prophet / dedicated ML forecasting service
- SSO (Azure AD / SAML)
- Encrypted portal credential vault

import { buildQuery, fetchApi, vehicleQuery } from "./client";
import type {
  Alert,
  BreakdownItem,
  DashboardSummary,
  ESOPerformance,
  InventoryItem,
  Order,
  PendencyStage,
  ShortageRisk,
  TATStage,
  TrendPoint,
} from "@/types";

export type AuthUser = {
  id: number;
  email: string;
  full_name: string;
  role: string;
  allowed_state_ids: number[] | null;
};

export const authApi = {
  platformInfo: () =>
    fetchApi<{ app: { name: string; tagline: string; company: string } }>("/auth/platform-info"),
  login: (email: string, password: string) =>
    fetchApi<{ access_token: string; token_type: string; user: AuthUser }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => fetchApi<AuthUser>("/auth/me"),
};

export const dashboardApi = {
  summary: (vehicleType: string | null = null) =>
    fetchApi<DashboardSummary>(`/dashboard/summary${vehicleQuery(vehicleType)}`),
};

export const revenueApi = {
  byState: (vehicleType: string | null) =>
    fetchApi<BreakdownItem[]>(`/revenue/by-state${vehicleQuery(vehicleType)}`),
  byOem: (vehicleType: string | null) =>
    fetchApi<BreakdownItem[]>(`/revenue/by-oem${vehicleQuery(vehicleType)}`),
  byPortal: () => fetchApi<BreakdownItem[]>("/revenue/by-portal"),
  byDealer: (vehicleType: string | null) =>
    fetchApi<Array<{ dealer_name: string; dealer_type: string; state_name: string; order_count: number; revenue: number }>>(
      `/revenue/by-dealer${vehicleQuery(vehicleType)}`
    ),
  profitability: (vehicleType: string | null) =>
    fetchApi<Array<BreakdownItem & { estimated_profit: number; margin_pct: number }>>(
      `/revenue/profitability${vehicleQuery(vehicleType)}`
    ),
  oemComparison: () =>
    fetchApi<Array<{ oem_name: string; new_revenue: number; old_revenue: number; new_orders: number; old_orders: number }>>(
      "/revenue/oem-comparison"
    ),
  trends: (granularity = "week", vehicleType: string | null = null) =>
    fetchApi<TrendPoint[]>(
      `/revenue/trends${buildQuery(vehicleType, { days: 90, granularity })}`
    ),
  stateOemMatrix: (vehicleType: string | null) =>
    fetchApi<Array<{ state: string; oem: string; order_count: number; revenue: number }>>(
      `/revenue/state-oem-matrix${vehicleQuery(vehicleType)}`
    ),
};

export const pendencyApi = {
  overview: (vehicleType: string | null) =>
    fetchApi<{ total_pending: number; total_delayed: number; delay_rate_pct: number }>(
      `/pendency/overview${vehicleQuery(vehicleType)}`
    ),
  byStage: (vehicleType: string | null) =>
    fetchApi<PendencyStage[]>(`/pendency/by-stage${vehicleQuery(vehicleType)}`),
  byState: (vehicleType: string | null) =>
    fetchApi<{ id: number; name: string; pending_count: number }[]>(
      `/pendency/by-state${vehicleQuery(vehicleType)}`
    ),
  byOem: (vehicleType: string | null) =>
    fetchApi<{ oem_name: string; pending_count: number }[]>(`/pendency/by-oem${vehicleQuery(vehicleType)}`),
  critical: () =>
    fetchApi<Array<{ order_number: string; stage: string; overdue_hours: number; vehicle_type: string }>>(
      "/pendency/critical"
    ),
  monthlyOverview: () => fetchApi<Array<Record<string, string | number>>>("/pendency/monthly-overview"),
};

export const performanceApi = {
  eso: (vehicleType: string | null) =>
    fetchApi<ESOPerformance[]>(`/performance/eso${vehicleQuery(vehicleType)}`),
  rejectionTrends: () =>
    fetchApi<{ period: string; rejection_count: number }[]>("/performance/rejections/trends"),
  stateActivity: () =>
    fetchApi<{ state_name: string; order_count: number; completed_count: number }[]>(
      "/performance/state-activity"
    ),
  dealerFrequency: () =>
    fetchApi<Array<{ dealer_name: string; dealer_type: string; state_name: string; order_count: number }>>(
      "/performance/dealer-frequency"
    ),
  monthlyEso: () =>
    fetchApi<Array<{ eso_name: string; orders_90d: number; completed_90d: number; completion_rate: number }>>(
      "/performance/monthly-eso"
    ),
};

export const inventoryApi = {
  overview: () => fetchApi<InventoryItem[]>("/inventory/overview"),
  shortageRisk: () => fetchApi<ShortageRisk[]>("/inventory/shortage-risk"),
  breakdown: () =>
    fetchApi<{ by_size: { size: string; quantity: number }[]; by_color: { color: string; quantity: number }[] }>(
      "/inventory/breakdown"
    ),
  oemConsumption: () => fetchApi<Array<{ oem_name: string; consumed_units: number }>>("/inventory/oem-consumption"),
  historicalConsumption: () =>
    fetchApi<Array<{ period: string; consumed: number }>>("/inventory/historical-consumption"),
};

export const tatApi = {
  byStage: (vehicleType: string | null) =>
    fetchApi<TATStage[]>(`/tat/by-stage${vehicleQuery(vehicleType)}`),
  byState: () =>
    fetchApi<{ state_name: string; avg_total_tat_hours: number; completed_orders: number }[]>("/tat/by-state"),
  byEso: () => fetchApi<Array<{ eso_name: string; avg_total_tat_hours: number; completed_orders: number }>>("/tat/by-eso"),
  recommendations: () =>
    fetchApi<Array<{ stage: string; avg_hours: number; recommendation: string }>>("/tat/recommendations"),
};

export const alertsApi = {
  list: (severity?: string) =>
    fetchApi<Alert[]>(`/alerts${severity ? `?severity=${severity}` : ""}`),
  generate: () => fetchApi<Alert[]>("/alerts/generate", { method: "POST" }),
};

export const ordersApi = {
  list: (vehicleType: string | null, limit = 20) =>
    fetchApi<Order[]>(`/orders${buildQuery(vehicleType, { limit })}`),
};

export const configApi = {
  ui: () =>
    fetchApi<{
      app: { name: string; tagline: string; company: string; description: string };
      vehicle_filters: { value: string; label: string }[];
      order_stages: { key: string; label: string }[];
      profit_margin_pct: number;
      llm_configured: boolean;
      llm_model: string | null;
      navigation: { title: string; path: string; icon: string }[];
      report_exports: { id: string; label: string; description: string }[];
      landing_features: { title: string; description: string; icon: string }[];
    }>("/config/ui"),
  dashboardMetrics: (vehicleType: string | null = null) =>
    fetchApi<{ metrics: Array<{ key: string; label: string; value: number; format: string }> }>(
      `/config/dashboard-metrics${vehicleQuery(vehicleType)}`
    ),
  monitoringMetrics: (vehicleType: string | null = null) =>
    fetchApi<{ metrics: Array<{ key: string; label: string; value: number; icon: string }> }>(
      `/config/monitoring-metrics${vehicleQuery(vehicleType)}`
    ),
};

export const monitoringApi = {
  live: (vehicleType: string | null = null) =>
    fetchApi<{
      total_active_orders: number;
      new_vehicle_live: number;
      old_vehicle_live: number;
      in_embossing: number;
      in_dispatch: number;
      in_fitment: number;
    }>(`/monitoring/live${vehicleQuery(vehicleType)}`),
  states: (vehicleType: string | null = null) =>
    fetchApi<Array<{ state_name: string; active_orders: number; new_vehicle: number; old_vehicle: number }>>(
      `/monitoring/states${vehicleQuery(vehicleType)}`
    ),
  esoWorkload: () =>
    fetchApi<Array<{ eso_name: string; state_name: string; pending_orders: number; load_pct: number; status: string }>>(
      "/monitoring/eso-workload"
    ),
  embossing: () => fetchApi<{ orders_in_embossing: number; delayed_count: number; avg_wait_hours: number }>(
    "/monitoring/embossing"
  ),
  dispatch: () => fetchApi<{ orders_in_dispatch: number; delayed_dispatch: number }>("/monitoring/dispatch"),
  dealers: () =>
    fetchApi<Array<{ dealer_name: string; dealer_type: string; state_name: string; order_count: number; revenue: number }>>(
      "/monitoring/dealers"
    ),
};

export const assistantApi = {
  ask: (question: string, vehicleType: string | null = null) =>
    fetchApi<{ answer: string; sources: string[]; llm_used?: boolean; model?: string }>("/assistant/ask", {
      method: "POST",
      body: JSON.stringify({ question, vehicle_type: vehicleType }),
    }),
  suggestions: (vehicleType: string | null = null) =>
    fetchApi<{ suggestions: string[] }>(
      `/assistant/suggestions${vehicleType ? `?vehicle_type=${vehicleType}` : ""}`
    ),
};

export const reportsApi = {
  summary: () =>
    fetchApi<{
      executive_summary: string;
      kpis: DashboardSummary;
      priority_alerts: Array<{ title: string; severity: string; message: string }>;
      recommendations: string[];
    }>("/reports/summary"),
  exportUrl: (type: string) => `/api/v1/reports/export/${type}`,
  exportPptUrl: () => `/api/v1/reports/export/executive-ppt`,
};

export const integrationsApi = {
  status: () =>
    fetchApi<{
      portals: Array<{ portal_name: string; configured: boolean; message: string }>;
    }>("/integrations/status"),
  sync: () =>
    fetchApi<{
      results: Array<{
        portal: string;
        status: string;
        fetched?: number;
        upserted?: number;
        message?: string;
      }>;
    }>("/integrations/sync", { method: "POST" }),
  clearSkippedLogs: () =>
    fetchApi<{ deleted: number }>("/integrations/sync/logs/skipped", { method: "DELETE" }),
  syncLogs: () =>
    fetchApi<
      Array<{
        id: number;
        portal_name: string;
        status: string;
        records_fetched: number;
        records_upserted: number;
        error_message: string | null;
        started_at: string;
      }>
    >("/integrations/sync/logs"),
};

export const planningApi = {
  forecastOrders: (vehicleType: string | null) =>
    fetchApi<{ history: TrendPoint[]; forecast: Array<{ period: string; forecast: number }> }>(
      `/planning/forecast/orders${vehicleQuery(vehicleType)}`
    ),
  forecastRevenue: () =>
    fetchApi<{ history: TrendPoint[]; forecast: Array<{ period: string; revenue: number }> }>(
      "/planning/forecast/revenue"
    ),
  festival: () =>
    fetchApi<Array<{ month: string; demand_multiplier: number; projected_orders: number; recommendation: string }>>(
      "/planning/forecast/festival"
    ),
  procurement: () =>
    fetchApi<Array<{ state_name: string; oem_name: string; plate_size?: string; order_quantity: number; priority: string }>>(
      "/planning/procurement"
    ),
  interstateBalancing: () =>
    fetchApi<Array<{ from_state: string; to_state: string; suggested_transfer_units: number; reason: string }>>(
      "/planning/interstate-balancing"
    ),
  minStockAlerts: () => fetchApi<InventoryItem[]>("/planning/minimum-stock-alerts"),
};

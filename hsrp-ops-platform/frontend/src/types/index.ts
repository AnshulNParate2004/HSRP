export interface DashboardSummary {
  total_orders: number;
  total_revenue: number;
  new_vehicle_orders: number;
  old_vehicle_orders: number;
  pending_orders: number;
  completed_orders: number;
  critical_alerts: number;
  avg_tat_hours: number;
  active_esos: number;
  active_oems: number;
  active_dealers?: number;
  metrics?: Array<{ key: string; label: string; value: number; format: string }>;
}

export interface BreakdownItem {
  id?: number;
  name: string;
  order_count: number;
  revenue: number;
  percentage?: number;
}

export interface TrendPoint {
  period: string;
  order_count: number;
  revenue: number;
  [key: string]: string | number;
}

export interface PendencyStage {
  stage: string;
  pending_count: number;
  delayed_count: number;
  sla_hours: number;
  avg_hours_in_stage: number;
}

export interface ESOPerformance {
  eso_id: number;
  eso_name: string;
  state_name: string;
  total_orders: number;
  completed_orders: number;
  completion_rate: number;
  rejection_count: number;
  avg_tat_hours: number;
}

export interface InventoryItem {
  id: number;
  warehouse_name: string;
  state_name: string;
  oem_name: string;
  plate_size: string;
  plate_color: string;
  quantity: number;
  reorder_level: number;
  days_of_stock: number | null;
  status: string;
}

export interface ShortageRisk {
  inventory_id: number;
  state_name: string;
  oem_name: string;
  plate_size: string;
  current_stock: number;
  projected_need_7d: number;
  gap: number;
  risk_level: string;
  recommendation: string;
}

export interface TATStage {
  stage: string;
  label: string;
  avg_hours: number;
  p90_hours: number;
  sample_count: number;
}

export interface Alert {
  id: number;
  alert_type: string;
  severity: string;
  title: string;
  message: string;
  recommendation: string | null;
  created_at: string;
}

export interface Order {
  id: number;
  order_number: string;
  vehicle_type: string;
  oem_name: string;
  state_name: string;
  eso_name: string | null;
  portal_name: string;
  revenue: number;
  current_stage: string;
  order_date: string;
  hours_in_current_stage: number;
}

export type VehicleFilter = "all" | "new" | "old";

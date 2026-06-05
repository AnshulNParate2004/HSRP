import { useQuery } from "@tanstack/react-query";
import {
  Package,
  IndianRupee,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Timer,
  Building2,
  Truck,
} from "lucide-react";
import { Link } from "react-router-dom";
import { dashboardApi, alertsApi, ordersApi, revenueApi, monitoringApi } from "@/lib/api";
import { useVehicleFilter } from "@/contexts/VehicleContext";
import { useOrderStages } from "@/hooks/useAppConfig";
import { MetricCards } from "@/components/dashboard/MetricCards";
import { PageHeader, SeverityBadge } from "@/components/ui/PageHeader";
import { PageLoader } from "@/components/ui/PageLoader";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency, formatNumber } from "@/lib/utils";
import { LineChartPanel } from "@/components/charts/ChartPanels";
import { StateHeatmap } from "@/components/maps/StateHeatmap";

const METRIC_ICONS: Record<string, { icon: typeof Package; color: string; bg: string }> = {
  total_orders: { icon: Package, color: "text-blue-600", bg: "bg-blue-500/10" },
  total_revenue: { icon: IndianRupee, color: "text-primary", bg: "bg-primary/10" },
  pending_orders: { icon: Clock, color: "text-amber-600", bg: "bg-amber-500/10" },
  completed_orders: { icon: CheckCircle2, color: "text-emerald-600", bg: "bg-emerald-500/10" },
  critical_alerts: { icon: AlertTriangle, color: "text-red-600", bg: "bg-red-500/10" },
  avg_tat_hours: { icon: Timer, color: "text-violet-600", bg: "bg-violet-500/10" },
  new_vehicle_orders: { icon: Truck, color: "text-sky-600", bg: "bg-sky-500/10" },
  old_vehicle_orders: { icon: Truck, color: "text-orange-600", bg: "bg-orange-500/10" },
  active_esos: { icon: Building2, color: "text-teal-600", bg: "bg-teal-500/10" },
  active_oems: { icon: Building2, color: "text-indigo-600", bg: "bg-indigo-500/10" },
};

function formatMetricValue(value: number, format: string): string | number {
  if (format === "currency") return formatCurrency(value);
  if (format === "decimal") return value;
  return formatNumber(value);
}

export default function Dashboard() {
  const { apiVehicleType, vehicleFilter } = useVehicleFilter();
  const stageLabels = useOrderStages();

  const { data: summary, isLoading, error } = useQuery({
    queryKey: ["dashboard-summary", apiVehicleType],
    queryFn: () => dashboardApi.summary(apiVehicleType),
  });

  const { data: alerts = [] } = useQuery({
    queryKey: ["alerts-top"],
    queryFn: () => alertsApi.list(),
  });

  const { data: orders = [] } = useQuery({
    queryKey: ["orders-recent", apiVehicleType],
    queryFn: () => ordersApi.list(apiVehicleType, 10),
  });

  const { data: trends = [] } = useQuery({
    queryKey: ["revenue-trends", apiVehicleType],
    queryFn: () => revenueApi.trends("week", apiVehicleType),
  });

  const { data: stateActivity = [] } = useQuery({
    queryKey: ["monitoring-states-dash", apiVehicleType],
    queryFn: () => monitoringApi.states(apiVehicleType),
  });

  if (isLoading) return <PageLoader />;
  if (error || !summary) {
    return <ErrorBanner message="Failed to load dashboard. Ensure the backend is running on port 8000." />;
  }

  const metrics = (summary.metrics ?? []).map((m) => {
    const style = METRIC_ICONS[m.key] ?? METRIC_ICONS.total_orders;
    return {
      label: m.label,
      value: formatMetricValue(m.value, m.format),
      icon: style.icon,
      color: style.color,
      bg: style.bg,
    };
  });

  const topAlerts = alerts.slice(0, 5);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Operations Dashboard"
        description={
          vehicleFilter === "all"
            ? "Real-time PAN India HSRP lifecycle monitoring — Real Industries Limited"
            : `Showing ${vehicleFilter === "new" ? "new vehicle" : "old vehicle"} orders only`
        }
      />

      <MetricCards metrics={metrics} />

      <StateHeatmap
        title="PAN India State Activity Heatmap"
        data={stateActivity.map((s) => ({ state_name: s.state_name, value: s.active_orders }))}
      />

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <LineChartPanel
            title="Weekly Order & Revenue Trends"
            data={trends}
            lines={[
              { key: "order_count", label: "Orders", color: "#3b82f6" },
              { key: "revenue", label: "Revenue (₹)", color: "#f97316" },
            ]}
          />
        </div>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>AI Alert Digest</CardTitle>
            <Link to="/app/alerts" className="text-xs text-primary font-medium hover:underline">
              View all
            </Link>
          </CardHeader>
          <CardContent className="space-y-3">
            {topAlerts.length === 0 ? (
              <p className="text-sm text-muted-foreground">No active alerts</p>
            ) : (
              topAlerts.map((a) => (
                <div key={a.id} className="rounded-lg border border-black/10 p-3 space-y-1">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-xs font-semibold leading-snug">{a.title}</p>
                    <SeverityBadge severity={a.severity} />
                  </div>
                  <p className="text-[11px] text-muted-foreground line-clamp-2">{a.message}</p>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Live Orders</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-black/10 text-left text-[11px] uppercase text-muted-foreground">
                <th className="pb-2 pr-4">Order #</th>
                <th className="pb-2 pr-4">State</th>
                <th className="pb-2 pr-4">OEM</th>
                <th className="pb-2 pr-4">Stage</th>
                <th className="pb-2 pr-4">Type</th>
                <th className="pb-2 pr-4">Revenue</th>
                <th className="pb-2">Hours in Stage</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id} className="border-b border-black/5 hover:bg-muted/30">
                  <td className="py-2.5 pr-4 font-mono text-xs">{o.order_number}</td>
                  <td className="py-2.5 pr-4">{o.state_name}</td>
                  <td className="py-2.5 pr-4">{o.oem_name}</td>
                  <td className="py-2.5 pr-4">{stageLabels[o.current_stage] ?? o.current_stage}</td>
                  <td className="py-2.5 pr-4 capitalize">{o.vehicle_type}</td>
                  <td className="py-2.5 pr-4">{formatCurrency(o.revenue)}</td>
                  <td className="py-2.5">{o.hours_in_current_stage}h</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}

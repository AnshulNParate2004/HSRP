import { useQuery } from "@tanstack/react-query";
import { planningApi } from "@/lib/api";
import { useVehicleFilter } from "@/contexts/VehicleContext";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLoader } from "@/components/ui/PageLoader";
import { LineChartPanel, BarChartPanel } from "@/components/charts/ChartPanels";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SeverityBadge } from "@/components/ui/PageHeader";

export default function PlanningPage() {
  const { apiVehicleType } = useVehicleFilter();

  const { data: orders, isLoading } = useQuery({
    queryKey: ["planning-orders", apiVehicleType],
    queryFn: () => planningApi.forecastOrders(apiVehicleType),
  });

  const { data: revenue } = useQuery({ queryKey: ["planning-revenue"], queryFn: planningApi.forecastRevenue });
  const { data: festival } = useQuery({ queryKey: ["planning-festival"], queryFn: planningApi.festival });
  const { data: procurement } = useQuery({ queryKey: ["planning-procurement"], queryFn: planningApi.procurement });
  const { data: balancing } = useQuery({ queryKey: ["planning-balancing"], queryFn: planningApi.interstateBalancing });
  const { data: minStock } = useQuery({ queryKey: ["planning-minstock"], queryFn: planningApi.minStockAlerts });

  if (isLoading) return <PageLoader />;

  const forecastData = [
    ...(orders?.history ?? []).map((h) => ({ period: h.period, actual: h.order_count, forecast: 0 })),
    ...(orders?.forecast ?? []).map((f) => ({ period: f.period, actual: 0, forecast: f.forecast })),
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Predictive Inventory Planning"
        description="Festival demand forecasting, replenishment recommendations, inter-state stock balancing"
      />

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg border-2 border-black/20 bg-card px-4 py-3">
          <p className="text-[10px] uppercase text-muted-foreground">Min Stock Alerts</p>
          <p className="text-2xl font-bold text-amber-600">{minStock?.length ?? 0}</p>
        </div>
        <div className="rounded-lg border-2 border-black/20 bg-card px-4 py-3">
          <p className="text-[10px] uppercase text-muted-foreground">Procurement Items</p>
          <p className="text-2xl font-bold">{procurement?.length ?? 0}</p>
        </div>
        <div className="rounded-lg border-2 border-black/20 bg-card px-4 py-3">
          <p className="text-[10px] uppercase text-muted-foreground">Inter-state Transfers</p>
          <p className="text-2xl font-bold">{balancing?.length ?? 0}</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <LineChartPanel
          title="Order Volume Forecast"
          data={forecastData}
          lines={[
            { key: "actual", label: "Historical", color: "#3b82f6" },
            { key: "forecast", label: "Forecast", color: "#f97316" },
          ]}
        />
        <LineChartPanel
          title="Revenue Forecast"
          data={[
            ...(revenue?.history ?? []).map((h) => ({ period: h.period, revenue: h.revenue })),
            ...(revenue?.forecast ?? []).map((f) => ({ period: f.period, revenue: f.revenue })),
          ]}
          lines={[{ key: "revenue", label: "Revenue (₹)", color: "#10b981" }]}
        />
      </div>

      <BarChartPanel
        title="Festival Demand Forecast"
        data={(festival ?? []).map((f) => ({ name: f.month, value: f.projected_orders }))}
        valueLabel="Projected Orders"
      />

      <Card>
        <CardHeader><CardTitle>Automated Replenishment Plan</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {(procurement ?? []).slice(0, 10).map((p, i) => (
            <div key={i} className="flex items-center justify-between rounded-lg border p-3 text-sm">
              <span>{p.state_name} — {p.oem_name}{p.plate_size ? ` (${p.plate_size})` : ""}</span>
              <div className="flex items-center gap-2">
                <span className="font-bold">{p.order_quantity} units</span>
                <SeverityBadge severity={p.priority === "critical" ? "critical" : "medium"} />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Inter-State Stock Balancing</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          {(balancing ?? []).map((b, i) => (
            <div key={i} className="rounded-lg border p-3 text-sm">
              <p className="font-medium">{b.from_state} → {b.to_state}: {b.suggested_transfer_units} units</p>
              <p className="text-xs text-muted-foreground">{b.reason}</p>
            </div>
          ))}
          {(balancing ?? []).length === 0 && (
            <p className="text-sm text-muted-foreground">No inter-state transfers recommended at this time.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

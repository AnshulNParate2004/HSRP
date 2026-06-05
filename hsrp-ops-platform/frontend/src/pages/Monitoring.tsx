import { useQuery } from "@tanstack/react-query";
import { Activity, Factory, Truck, Users } from "lucide-react";
import { monitoringApi, configApi } from "@/lib/api";
import { useVehicleFilter } from "@/contexts/VehicleContext";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLoader } from "@/components/ui/PageLoader";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { StateHeatmap } from "@/components/maps/StateHeatmap";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency } from "@/lib/utils";
import { getNavIcon } from "@/lib/navIcons";

const ICON_FALLBACK: Record<string, typeof Activity> = {
  Activity,
  Truck,
  Factory,
  Users,
};

export default function MonitoringPage() {
  const { apiVehicleType } = useVehicleFilter();

  const { data: live, isLoading, error } = useQuery({
    queryKey: ["monitoring-live", apiVehicleType],
    queryFn: () => monitoringApi.live(apiVehicleType),
    refetchInterval: 30000,
  });

  const { data: metricDefs } = useQuery({
    queryKey: ["monitoring-metrics", apiVehicleType],
    queryFn: () => configApi.monitoringMetrics(apiVehicleType),
  });

  const { data: states } = useQuery({
    queryKey: ["monitoring-states", apiVehicleType],
    queryFn: () => monitoringApi.states(apiVehicleType),
  });
  const { data: esoWorkload } = useQuery({ queryKey: ["monitoring-eso"], queryFn: monitoringApi.esoWorkload });
  const { data: embossing } = useQuery({ queryKey: ["monitoring-embossing"], queryFn: monitoringApi.embossing });
  const { data: dispatch } = useQuery({ queryKey: ["monitoring-dispatch"], queryFn: monitoringApi.dispatch });
  const { data: dealers } = useQuery({ queryKey: ["monitoring-dealers"], queryFn: monitoringApi.dealers });

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorBanner message="Failed to load monitoring data." />;

  const metrics = (metricDefs?.metrics ?? []).map((m) => {
    const Icon = ICON_FALLBACK[m.icon] ?? getNavIcon(m.icon);
    return {
      label: m.label,
      value: m.value,
      icon: Icon,
      color: "text-primary",
      bg: "bg-primary/10",
    };
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Real-Time Monitoring"
        description="Live operational dashboard — new & old vehicle orders, ESO workload, embossing, dispatch, dealers"
      />

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
        {metrics.map((m) => (
          <div key={m.label} className="rounded-lg border-2 border-black/20 bg-card px-4 py-3 flex items-center gap-3">
            <div className={`w-9 h-9 rounded-lg ${m.bg} ${m.color} flex items-center justify-center`}>
              <m.icon className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[10px] uppercase text-muted-foreground">{m.label}</p>
              <p className="text-xl font-bold">{m.value}</p>
            </div>
          </div>
        ))}
      </div>

      <StateHeatmap
        title="Geo-based State Activity (Active Orders)"
        data={(states ?? []).map((s) => ({ state_name: s.state_name, value: s.active_orders }))}
      />

      <div className="grid lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle>Embossing Station Monitor</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p>Orders in embossing: <strong>{embossing?.orders_in_embossing ?? 0}</strong></p>
            <p>Delayed: <strong className="text-red-600">{embossing?.delayed_count ?? 0}</strong></p>
            <p>Avg wait: <strong>{embossing?.avg_wait_hours ?? 0}h</strong></p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Dispatch Monitor</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm">
            <p>In dispatch: <strong>{dispatch?.orders_in_dispatch ?? 0}</strong></p>
            <p>Delayed dispatch: <strong className="text-red-600">{dispatch?.delayed_dispatch ?? 0}</strong></p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>ESO Workload Visibility</CardTitle></CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-[11px] uppercase text-muted-foreground">
                <th className="pb-2 pr-4">ESO</th>
                <th className="pb-2 pr-4">State</th>
                <th className="pb-2 pr-4">Pending</th>
                <th className="pb-2 pr-4">Load</th>
                <th className="pb-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {(esoWorkload ?? []).slice(0, 15).map((e) => (
                <tr key={e.eso_name} className="border-b border-black/5">
                  <td className="py-2 pr-4">{e.eso_name}</td>
                  <td className="py-2 pr-4">{e.state_name}</td>
                  <td className="py-2 pr-4">{e.pending_orders}</td>
                  <td className="py-2 pr-4">{e.load_pct}%</td>
                  <td className="py-2 capitalize">{e.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Dealer & Fitment Center Activity</CardTitle></CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-[11px] uppercase text-muted-foreground">
                <th className="pb-2 pr-4">Dealer</th>
                <th className="pb-2 pr-4">Type</th>
                <th className="pb-2 pr-4">State</th>
                <th className="pb-2 pr-4">Orders</th>
                <th className="pb-2">Revenue</th>
              </tr>
            </thead>
            <tbody>
              {(dealers ?? []).map((d) => (
                <tr key={d.dealer_name} className="border-b border-black/5">
                  <td className="py-2 pr-4">{d.dealer_name}</td>
                  <td className="py-2 pr-4 capitalize">{d.dealer_type}</td>
                  <td className="py-2 pr-4">{d.state_name}</td>
                  <td className="py-2 pr-4">{d.order_count}</td>
                  <td className="py-2">{formatCurrency(d.revenue)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}

import { useQuery } from "@tanstack/react-query";
import { pendencyApi } from "@/lib/api";
import { useVehicleFilter } from "@/contexts/VehicleContext";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLoader } from "@/components/ui/PageLoader";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { BarChartPanel } from "@/components/charts/ChartPanels";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useOrderStages } from "@/hooks/useAppConfig";

export default function PendencyPage() {
  const { apiVehicleType } = useVehicleFilter();
  const stageLabels = useOrderStages();

  const { data: overview, isLoading, error } = useQuery({
    queryKey: ["pendency-overview", apiVehicleType],
    queryFn: () => pendencyApi.overview(apiVehicleType),
  });

  const { data: byStage } = useQuery({
    queryKey: ["pendency-by-stage", apiVehicleType],
    queryFn: () => pendencyApi.byStage(apiVehicleType),
  });

  const { data: byState } = useQuery({
    queryKey: ["pendency-by-state", apiVehicleType],
    queryFn: () => pendencyApi.byState(apiVehicleType),
  });

  const { data: critical } = useQuery({
    queryKey: ["pendency-critical"],
    queryFn: pendencyApi.critical,
  });

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorBanner message="Failed to load pendency data." />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Pendency & Delay Monitor"
        description="Stage-wise bottlenecks and SLA breach tracking"
      />

      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Total Pending", value: overview?.total_pending ?? 0 },
          { label: "Delayed", value: overview?.total_delayed ?? 0 },
          { label: "Delay Rate", value: `${overview?.delay_rate_pct ?? 0}%` },
        ].map((k) => (
          <div key={k.label} className="rounded-lg border-2 border-black/20 bg-card px-4 py-3">
            <p className="text-[10px] uppercase text-muted-foreground font-medium">{k.label}</p>
            <p className="text-2xl font-bold">{k.value}</p>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <BarChartPanel
          title="Pending by Stage"
          data={(byStage ?? []).map((s) => ({
            name: stageLabels[s.stage]?.replace(" Pending", "") ?? s.stage,
            value: s.pending_count,
            secondary: s.delayed_count,
          }))}
          valueLabel="Pending"
          secondaryKey="secondary"
          secondaryLabel="Delayed"
        />
        <BarChartPanel
          title="Pending by State"
          data={(byState ?? []).slice(0, 10).map((s) => ({ name: s.name, value: s.pending_count }))}
          valueLabel="Pending Orders"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Critical SLA Breaches</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-[11px] uppercase text-muted-foreground">
                <th className="pb-2 pr-4">Order #</th>
                <th className="pb-2 pr-4">Stage</th>
                <th className="pb-2 pr-4">Overdue (hrs)</th>
                <th className="pb-2">Type</th>
              </tr>
            </thead>
            <tbody>
              {(critical ?? []).slice(0, 15).map((c, i) => (
                <tr key={i} className="border-b border-black/5">
                  <td className="py-2 pr-4 font-mono text-xs">{c.order_number}</td>
                  <td className="py-2 pr-4">{stageLabels[c.stage] ?? c.stage}</td>
                  <td className="py-2 pr-4 text-red-600 font-semibold">{c.overdue_hours}h</td>
                  <td className="py-2 capitalize">{c.vehicle_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}

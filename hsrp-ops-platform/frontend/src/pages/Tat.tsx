import { useQuery } from "@tanstack/react-query";
import { tatApi } from "@/lib/api";
import { useVehicleFilter } from "@/contexts/VehicleContext";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLoader } from "@/components/ui/PageLoader";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { BarChartPanel } from "@/components/charts/ChartPanels";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function TatPage() {
  const { apiVehicleType } = useVehicleFilter();

  const { data: byStage, isLoading, error } = useQuery({
    queryKey: ["tat-by-stage", apiVehicleType],
    queryFn: () => tatApi.byStage(apiVehicleType),
  });

  const { data: byState } = useQuery({
    queryKey: ["tat-by-state"],
    queryFn: tatApi.byState,
  });

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorBanner message="Failed to load TAT data." />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="TAT Analysis"
        description="Turnaround time benchmarks across the HSRP lifecycle"
      />

      <BarChartPanel
        title="Average TAT by Stage (hours)"
        data={(byStage ?? [])
          .filter((s) => s.sample_count > 0)
          .map((s) => ({ name: s.label.replace(" → ", "→"), value: s.avg_hours, secondary: s.p90_hours }))}
        valueLabel="Avg Hours"
        secondaryKey="secondary"
        secondaryLabel="P90 Hours"
      />

      <Card>
        <CardHeader>
          <CardTitle>Stage-wise TAT Detail</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-[11px] uppercase text-muted-foreground">
                <th className="pb-2 pr-4">Stage</th>
                <th className="pb-2 pr-4">Avg (hrs)</th>
                <th className="pb-2 pr-4">P90 (hrs)</th>
                <th className="pb-2">Samples</th>
              </tr>
            </thead>
            <tbody>
              {(byStage ?? []).map((s) => (
                <tr key={s.stage} className="border-b border-black/5">
                  <td className="py-2 pr-4">{s.label}</td>
                  <td className="py-2 pr-4 font-semibold">{s.avg_hours}</td>
                  <td className="py-2 pr-4">{s.p90_hours}</td>
                  <td className="py-2">{s.sample_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <BarChartPanel
        title="Total TAT by State (completed orders)"
        data={(byState ?? [])
          .filter((s) => s.completed_orders > 0)
          .slice(0, 12)
          .map((s) => ({ name: s.state_name, value: s.avg_total_tat_hours }))}
        valueLabel="Avg Total TAT (hrs)"
      />
    </div>
  );
}

import { useQuery } from "@tanstack/react-query";
import { performanceApi } from "@/lib/api";
import { useVehicleFilter } from "@/contexts/VehicleContext";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLoader } from "@/components/ui/PageLoader";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { BarChartPanel, LineChartPanel } from "@/components/charts/ChartPanels";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function PerformancePage() {
  const { apiVehicleType } = useVehicleFilter();

  const { data: eso, isLoading, error } = useQuery({
    queryKey: ["performance-eso", apiVehicleType],
    queryFn: () => performanceApi.eso(apiVehicleType),
  });

  const { data: rejections } = useQuery({
    queryKey: ["rejection-trends"],
    queryFn: performanceApi.rejectionTrends,
  });

  const { data: stateActivity } = useQuery({
    queryKey: ["state-activity"],
    queryFn: performanceApi.stateActivity,
  });

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorBanner message="Failed to load performance data." />;

  const bottomEsos = [...(eso ?? [])].slice(0, 10);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Operational Performance"
        description="ESO productivity, rejection analytics, and state activity"
      />

      <div className="grid lg:grid-cols-2 gap-4">
        <BarChartPanel
          title="ESO Completion Rate (Bottom 10)"
          data={bottomEsos.map((e) => ({ name: e.eso_name.split("-").pop() ?? e.eso_name, value: e.completion_rate }))}
          valueLabel="Completion %"
        />
        <LineChartPanel
          title="Rejection Trends (Weekly)"
          data={rejections ?? []}
          lines={[{ key: "rejection_count", label: "Rejections", color: "#ef4444" }]}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>ESO Performance Leaderboard</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-[11px] uppercase text-muted-foreground">
                <th className="pb-2 pr-4">ESO</th>
                <th className="pb-2 pr-4">State</th>
                <th className="pb-2 pr-4">Orders</th>
                <th className="pb-2 pr-4">Completed</th>
                <th className="pb-2 pr-4">Rate</th>
                <th className="pb-2 pr-4">Rejections</th>
                <th className="pb-2">Avg TAT</th>
              </tr>
            </thead>
            <tbody>
              {(eso ?? []).slice(0, 20).map((e) => (
                <tr key={e.eso_id} className="border-b border-black/5">
                  <td className="py-2 pr-4 font-medium">{e.eso_name}</td>
                  <td className="py-2 pr-4">{e.state_name}</td>
                  <td className="py-2 pr-4">{e.total_orders}</td>
                  <td className="py-2 pr-4">{e.completed_orders}</td>
                  <td className="py-2 pr-4">
                    <span className={e.completion_rate >= 80 ? "text-emerald-600" : "text-amber-600"}>
                      {e.completion_rate}%
                    </span>
                  </td>
                  <td className="py-2 pr-4">{e.rejection_count}</td>
                  <td className="py-2">{e.avg_tat_hours}h</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <BarChartPanel
        title="State Operational Activity"
        data={(stateActivity ?? []).slice(0, 10).map((s) => ({
          name: s.state_name,
          value: s.order_count,
          secondary: s.completed_count,
        }))}
        valueLabel="Total Orders"
        secondaryKey="secondary"
        secondaryLabel="Completed"
      />
    </div>
  );
}

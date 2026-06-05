import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { RefreshCw } from "lucide-react";
import { alertsApi } from "@/lib/api";
import { PageHeader, SeverityBadge } from "@/components/ui/PageHeader";
import { PageLoader } from "@/components/ui/PageLoader";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { Card, CardContent } from "@/components/ui/card";

export default function AlertsPage() {
  const queryClient = useQueryClient();

  const { data: alerts, isLoading, error } = useQuery({
    queryKey: ["alerts-all"],
    queryFn: () => alertsApi.list(),
  });

  const regenerate = useMutation({
    mutationFn: () => alertsApi.generate(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts-all"] });
      queryClient.invalidateQueries({ queryKey: ["alerts-top"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorBanner message="Failed to load alerts." />;

  const grouped = {
    critical: alerts?.filter((a) => a.severity === "critical") ?? [],
    high: alerts?.filter((a) => a.severity === "high") ?? [],
    medium: alerts?.filter((a) => a.severity === "medium") ?? [],
    low: alerts?.filter((a) => a.severity === "low") ?? [],
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <PageHeader
          title="AI Smart Alerts"
          description="Predictive intelligence and exception-based management alerts"
        />
        <button
          onClick={() => regenerate.mutate()}
          disabled={regenerate.isPending}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-primary text-primary-foreground border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:opacity-90 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${regenerate.isPending ? "animate-spin" : ""}`} />
          Regenerate
        </button>
      </div>

      <div className="grid grid-cols-4 gap-3">
        {Object.entries(grouped).map(([sev, items]) => (
          <div key={sev} className="rounded-lg border-2 border-black/20 bg-card px-4 py-3 text-center">
            <SeverityBadge severity={sev} />
            <p className="text-2xl font-bold mt-2">{items.length}</p>
          </div>
        ))}
      </div>

      <div className="space-y-3">
        {alerts?.map((a) => (
          <Card key={a.id}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <SeverityBadge severity={a.severity} />
                    <span className="text-[10px] uppercase text-muted-foreground font-medium">{a.alert_type.replace(/_/g, " ")}</span>
                  </div>
                  <p className="font-semibold">{a.title}</p>
                  <p className="text-sm text-muted-foreground">{a.message}</p>
                  {a.recommendation && (
                    <p className="text-xs text-primary mt-2">→ {a.recommendation}</p>
                  )}
                </div>
                <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                  {new Date(a.created_at).toLocaleDateString()}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

import { useQuery } from "@tanstack/react-query";
import { Download, FileText } from "lucide-react";
import { reportsApi } from "@/lib/api";
import { useAppConfig } from "@/hooks/useAppConfig";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLoader } from "@/components/ui/PageLoader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SeverityBadge } from "@/components/ui/PageHeader";
import { formatCurrency, formatNumber } from "@/lib/utils";
import { downloadAuthenticatedFile } from "@/lib/download";

export default function ReportsPage() {
  const { data: config } = useAppConfig();

  const { data: summary, isLoading } = useQuery({
    queryKey: ["reports-summary"],
    queryFn: reportsApi.summary,
  });

  const reports = config?.report_exports ?? [];

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Reports & MIS Exports"
        description="Downloadable reports and automated management summaries"
      />

      <Card className="border-2 border-primary/20">
        <CardHeader><CardTitle>Executive Management Summary</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm leading-relaxed">{summary?.executive_summary}</p>
          {summary?.kpis && (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-[10px] uppercase text-muted-foreground">Orders</p>
                <p className="text-lg font-bold">{formatNumber(summary.kpis.total_orders)}</p>
              </div>
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-[10px] uppercase text-muted-foreground">Revenue</p>
                <p className="text-lg font-bold">{formatCurrency(summary.kpis.total_revenue)}</p>
              </div>
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-[10px] uppercase text-muted-foreground">Pending</p>
                <p className="text-lg font-bold">{summary.kpis.pending_orders}</p>
              </div>
              <div className="rounded-lg bg-muted/50 p-3">
                <p className="text-[10px] uppercase text-muted-foreground">Alerts</p>
                <p className="text-lg font-bold text-red-600">{summary.kpis.critical_alerts}</p>
              </div>
            </div>
          )}
          {summary?.recommendations && summary.recommendations.length > 0 && (
            <div>
              <p className="text-xs font-semibold uppercase text-muted-foreground mb-2">AI Recommendations</p>
              <ul className="space-y-1">
                {summary.recommendations.map((r, i) => (
                  <li key={i} className="text-sm text-primary">→ {r}</li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="border-2 border-primary/20">
        <CardContent className="p-4 flex items-center justify-between gap-4">
          <div>
            <p className="font-semibold text-sm">Executive PowerPoint</p>
            <p className="text-xs text-muted-foreground">Management MIS deck — KPIs, alerts, top states</p>
          </div>
          <button
            type="button"
            onClick={() =>
              downloadAuthenticatedFile(reportsApi.exportPptUrl(), "hsrp_executive_summary.pptx")
            }
            className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-primary text-primary-foreground border-2 border-black"
          >
            <Download className="h-4 w-4" /> Download PPT
          </button>
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {reports.map((r) => (
          <Card key={r.id}>
            <CardContent className="p-4 flex flex-col gap-3">
              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-primary shrink-0" />
                <div>
                  <p className="font-semibold text-sm">{r.label}</p>
                  <p className="text-xs text-muted-foreground">{r.description}</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() =>
                  downloadAuthenticatedFile(
                    reportsApi.exportUrl(r.id),
                    `${r.id}_report.csv`
                  )
                }
                className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline text-left"
              >
                <Download className="h-4 w-4" /> Download CSV
              </button>
            </CardContent>
          </Card>
        ))}
      </div>

      {summary?.priority_alerts && summary.priority_alerts.length > 0 && (
        <Card>
          <CardHeader><CardTitle>Priority Alerts</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {summary.priority_alerts.map((a, i) => (
              <div key={i} className="flex items-start gap-2 rounded-lg border p-3">
                <SeverityBadge severity={a.severity} />
                <div>
                  <p className="text-sm font-medium">{a.title}</p>
                  <p className="text-xs text-muted-foreground">{a.message}</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

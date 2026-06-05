import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, AlertCircle, CheckCircle2 } from "lucide-react";
import { integrationsApi } from "@/lib/api";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLoader } from "@/components/ui/PageLoader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/contexts/AuthContext";

export default function IntegrationsPage() {
  const { user } = useAuth();
  const qc = useQueryClient();
  const canSync = user?.role === "admin" || user?.role === "operations_manager";
  const isAdmin = user?.role === "admin";

  const { data: status } = useQuery({
    queryKey: ["integration-status"],
    queryFn: integrationsApi.status,
    staleTime: 60_000,
  });

  const { data: logs, isLoading } = useQuery({
    queryKey: ["integration-logs"],
    queryFn: integrationsApi.syncLogs,
    staleTime: 30_000,
    refetchOnWindowFocus: false,
  });

  const syncMutation = useMutation({
    mutationFn: integrationsApi.sync,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["integration-logs"] });
      qc.invalidateQueries({ queryKey: ["integration-status"] });
    },
  });

  const clearMutation = useMutation({
    mutationFn: integrationsApi.clearSkippedLogs,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["integration-logs"] }),
  });

  const configuredCount = status?.portals?.filter((p) => p.configured).length ?? 0;

  if (isLoading) return <PageLoader />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="OEM Portal Integrations"
        description="Live sync from DISHA, Hero Biz, Old Vehicle Portal, and POS"
        action={
          canSync ? (
            <div className="flex gap-2">
              {isAdmin && (
                <button
                  type="button"
                  onClick={() => clearMutation.mutate()}
                  disabled={clearMutation.isPending}
                  className="px-3 py-2 text-sm font-medium rounded-lg border-2 border-black/30 hover:bg-muted"
                >
                  Clear old skipped logs
                </button>
              )}
              <button
                type="button"
                onClick={() => syncMutation.mutate()}
                disabled={syncMutation.isPending}
                className="flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg bg-primary text-primary-foreground border-2 border-black"
              >
                <RefreshCw className={`w-4 h-4 ${syncMutation.isPending ? "animate-spin" : ""}`} />
                Sync now
              </button>
            </div>
          ) : undefined
        }
      />

      <div className="rounded-lg border-2 border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        <strong>Why “Skipped”?</strong> Portal APIs are not set in <code className="text-xs">backend/.env</code> yet.
        Auto-sync is <strong>off</strong> until you add URLs/keys and set{" "}
        <code className="text-xs">PORTAL_AUTO_SYNC=true</code>. “Sync now” only hits configured portals.
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {(status?.portals ?? []).map((p) => (
          <Card key={p.portal_name}>
            <CardContent className="p-4 flex items-start gap-3">
              {p.configured ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              ) : (
                <AlertCircle className="w-5 h-5 text-amber-600 shrink-0" />
              )}
              <div>
                <p className="font-semibold text-sm">{p.portal_name}</p>
                <p className="text-xs text-muted-foreground mt-1">{p.message}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {syncMutation.data?.results && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Last sync result</CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-1">
            {syncMutation.data.results.map((r) => (
              <p key={r.portal}>
                <strong>{r.portal}</strong>: {r.status}
                {r.status === "skipped" && " — configure API in .env"}
                {r.fetched != null && r.status !== "skipped" && ` (${r.fetched} fetched, ${r.upserted} upserted)`}
              </p>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Sync history</CardTitle>
          <p className="text-xs text-muted-foreground">
            Only real sync attempts are logged ({configuredCount}/4 portals configured)
          </p>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          {(logs ?? []).length > 0 ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-[11px] uppercase text-muted-foreground">
                  <th className="pb-2 pr-4">Portal</th>
                  <th className="pb-2 pr-4">Status</th>
                  <th className="pb-2 pr-4">Fetched</th>
                  <th className="pb-2 pr-4">Upserted</th>
                  <th className="pb-2">Started</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} className="border-b border-black/5">
                    <td className="py-2 pr-4">{log.portal_name}</td>
                    <td className="py-2 pr-4 capitalize">{log.status}</td>
                    <td className="py-2 pr-4">{log.records_fetched}</td>
                    <td className="py-2 pr-4">{log.records_upserted}</td>
                    <td className="py-2 text-xs">{new Date(log.started_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-sm text-muted-foreground py-4">
              No sync runs yet. Configure portal APIs, then click Sync now.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

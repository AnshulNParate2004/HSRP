import { useQuery } from "@tanstack/react-query";
import { inventoryApi } from "@/lib/api";
import { PageHeader, StatusBadge } from "@/components/ui/PageHeader";
import { PageLoader } from "@/components/ui/PageLoader";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { BarChartPanel, PieChartPanel } from "@/components/charts/ChartPanels";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function InventoryPage() {
  const { data: items, isLoading, error } = useQuery({
    queryKey: ["inventory-overview"],
    queryFn: inventoryApi.overview,
  });

  const { data: shortage } = useQuery({
    queryKey: ["inventory-shortage"],
    queryFn: inventoryApi.shortageRisk,
  });

  const { data: breakdown } = useQuery({
    queryKey: ["inventory-breakdown"],
    queryFn: inventoryApi.breakdown,
  });

  if (isLoading) return <PageLoader />;
  if (error) return <ErrorBanner message="Failed to load inventory data." />;

  const lowCount = (items ?? []).filter((i) => i.status !== "ok").length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Stock & Inventory Analytics"
        description="Real-time stock levels, consumption, and shortage prediction"
      />

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg border-2 border-black/20 bg-card px-4 py-3">
          <p className="text-[10px] uppercase text-muted-foreground">Total SKUs</p>
          <p className="text-2xl font-bold">{items?.length ?? 0}</p>
        </div>
        <div className="rounded-lg border-2 border-black/20 bg-card px-4 py-3">
          <p className="text-[10px] uppercase text-muted-foreground">Low / Critical Stock</p>
          <p className="text-2xl font-bold text-amber-600">{lowCount}</p>
        </div>
        <div className="rounded-lg border-2 border-black/20 bg-card px-4 py-3">
          <p className="text-[10px] uppercase text-muted-foreground">Shortage Risks (7d)</p>
          <p className="text-2xl font-bold text-red-600">{shortage?.length ?? 0}</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <PieChartPanel
          title="Stock by Plate Size"
          data={(breakdown?.by_size ?? []).map((s) => ({ name: s.size, value: s.quantity }))}
        />
        <PieChartPanel
          title="Stock by Color"
          data={(breakdown?.by_color ?? []).map((c) => ({ name: c.color, value: c.quantity }))}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>7-Day Shortage Risk</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {(shortage ?? []).slice(0, 8).map((s) => (
            <div key={s.inventory_id} className="rounded-lg border border-black/10 p-3 flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold">{s.state_name} — {s.oem_name}</p>
                <p className="text-xs text-muted-foreground">{s.plate_size} · Stock: {s.current_stock} · Need: {s.projected_need_7d}</p>
                <p className="text-xs text-primary mt-1">{s.recommendation}</p>
              </div>
              <StatusBadge status={s.risk_level === "critical" ? "critical" : s.risk_level === "high" ? "low" : "ok"} />
            </div>
          ))}
        </CardContent>
      </Card>

      <BarChartPanel
        title="Top Stock Levels by State (sample)"
        data={(items ?? [])
          .reduce<{ name: string; value: number }[]>((acc, item) => {
            const existing = acc.find((a) => a.name === item.state_name);
            if (existing) existing.value += item.quantity;
            else acc.push({ name: item.state_name, value: item.quantity });
            return acc;
          }, [])
          .sort((a, b) => b.value - a.value)
          .slice(0, 10)}
        valueLabel="Units in Stock"
      />
    </div>
  );
}

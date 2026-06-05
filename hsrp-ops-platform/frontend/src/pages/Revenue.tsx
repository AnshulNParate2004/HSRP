import { useQuery } from "@tanstack/react-query";
import { revenueApi } from "@/lib/api";
import { useVehicleFilter } from "@/contexts/VehicleContext";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLoader } from "@/components/ui/PageLoader";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { BarChartPanel, PieChartPanel, LineChartPanel } from "@/components/charts/ChartPanels";
import { formatCurrency } from "@/lib/utils";
import { useAppConfig } from "@/hooks/useAppConfig";

export default function RevenuePage() {
  const { apiVehicleType, vehicleFilter } = useVehicleFilter();
  const { data: config } = useAppConfig();
  const marginPct = Math.round((config?.profit_margin_pct ?? 0.22) * 100);

  const { data: byState, isLoading: s1, error: e1 } = useQuery({
    queryKey: ["revenue-by-state", apiVehicleType],
    queryFn: () => revenueApi.byState(apiVehicleType),
  });

  const { data: byOem } = useQuery({
    queryKey: ["revenue-by-oem", apiVehicleType],
    queryFn: () => revenueApi.byOem(apiVehicleType),
  });

  const { data: byPortal } = useQuery({
    queryKey: ["revenue-by-portal"],
    queryFn: revenueApi.byPortal,
  });

  const { data: trends } = useQuery({
    queryKey: ["revenue-trends"],
    queryFn: () => revenueApi.trends("week"),
  });

  const { data: dealers } = useQuery({
    queryKey: ["revenue-dealers", apiVehicleType],
    queryFn: () => revenueApi.byDealer(apiVehicleType),
  });

  const { data: profitability } = useQuery({
    queryKey: ["revenue-profit", apiVehicleType],
    queryFn: () => revenueApi.profitability(apiVehicleType),
  });

  const { data: oemCompare } = useQuery({
    queryKey: ["revenue-oem-compare"],
    queryFn: revenueApi.oemComparison,
  });

  if (s1) return <PageLoader />;
  if (e1) return <ErrorBanner message="Failed to load revenue analytics." />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Revenue Analytics"
        description={
          vehicleFilter === "all"
            ? "State-wise, OEM-wise, and portal-wise revenue contribution"
            : `${vehicleFilter === "new" ? "New" : "Old"} vehicle revenue only`
        }
      />

      <div className="grid lg:grid-cols-2 gap-4">
        <BarChartPanel
          title="Revenue by State"
          data={(byState ?? []).slice(0, 10).map((s) => ({ name: s.name, value: s.revenue, secondary: s.order_count }))}
          valueLabel="Revenue (₹)"
          secondaryKey="secondary"
          secondaryLabel="Orders"
          formatValue={(v) => formatCurrency(v)}
        />
        <BarChartPanel
          title="Revenue by OEM"
          data={(byOem ?? []).slice(0, 8).map((o) => ({ name: o.name, value: o.revenue }))}
          valueLabel="Revenue (₹)"
          formatValue={(v) => formatCurrency(v)}
        />
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <PieChartPanel
          title="Portal Contribution"
          data={(byPortal ?? []).map((p) => ({ name: p.name, value: p.revenue }))}
        />
        <LineChartPanel
          title="Order Volume Trend (Weekly)"
          data={trends ?? []}
          lines={[{ key: "order_count", label: "Orders", color: "#3b82f6" }]}
        />
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <BarChartPanel
          title="Dealer & Fitment Center Contribution"
          data={(dealers ?? []).slice(0, 8).map((d) => ({ name: d.dealer_name.split(" ").slice(-2).join(" "), value: d.revenue }))}
          valueLabel="Revenue (₹)"
          formatValue={(v) => formatCurrency(v)}
        />
        <BarChartPanel
          title={`State Profitability (Est. ${marginPct}% margin)`}
          data={(profitability ?? []).slice(0, 8).map((s) => ({ name: s.name, value: s.estimated_profit }))}
          valueLabel="Profit (₹)"
          formatValue={(v) => formatCurrency(v)}
        />
      </div>

      <BarChartPanel
        title="OEM Comparison — New vs Old Vehicle Revenue"
        data={(oemCompare ?? []).slice(0, 6).map((o) => ({
          name: o.oem_name,
          value: o.new_revenue,
          secondary: o.old_revenue,
        }))}
        valueLabel="New Vehicle ₹"
        secondaryKey="secondary"
        secondaryLabel="Old Vehicle ₹"
        formatValue={(v) => formatCurrency(v)}
      />
    </div>
  );
}

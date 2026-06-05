import { useMemo } from "react";
import { IndiaGeoMap } from "./IndiaGeoMap";
import { heatClass, type StateMapDatum } from "./indiaGeoUtils";

interface StateHeatmapProps {
  data: StateMapDatum[];
  title?: string;
}

export function StateHeatmap({ data, title = "State Heatmap" }: StateHeatmapProps) {
  const max = useMemo(() => Math.max(...data.map((d) => d.value), 1), [data]);
  const topStates = useMemo(
    () => [...data].sort((a, b) => b.value - a.value).slice(0, 8),
    [data],
  );

  return (
    <div className="rounded-xl border-2 border-black/20 bg-card p-5">
      <h3 className="text-base font-bold mb-4">{title}</h3>

      <div className="grid lg:grid-cols-[1fr_220px] gap-4 items-start">
        <IndiaGeoMap data={data} />

        <div className="space-y-2">
          <p className="text-[10px] uppercase font-semibold text-muted-foreground tracking-wide">
            Top states
          </p>
          {topStates.map((d) => (
            <div
              key={d.state_name}
              className={`rounded-lg px-3 py-2 border border-black/10 ${heatClass(d.value, max)}`}
            >
              <p className="text-[11px] font-medium truncate">{d.state_name}</p>
              <p className="text-sm font-bold">{d.label ?? d.value}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2 mt-4 text-[10px] text-muted-foreground">
        <span>Low</span>
        <div className="flex-1 h-2 rounded-full bg-gradient-to-r from-emerald-200 via-amber-300 via-orange-400 to-red-500" />
        <span>High</span>
      </div>
    </div>
  );
}

export interface StateMapDatum {
  state_name: string;
  value: number;
  label?: string;
}

export function normalizeStateName(name: string): string {
  return name.trim().toLowerCase();
}

export function buildValueLookup(data: StateMapDatum[]): Map<string, StateMapDatum> {
  const map = new Map<string, StateMapDatum>();
  for (const item of data) {
    map.set(normalizeStateName(item.state_name), item);
  }
  return map;
}

/** Choropleth fill from low (green) to high (red). */
export function heatFill(value: number, max: number): string {
  if (max <= 0 || value <= 0) return "#e2e8f0";
  const pct = value / max;
  if (pct > 0.75) return "#ef4444";
  if (pct > 0.5) return "#fb923c";
  if (pct > 0.25) return "#fcd34d";
  return "#6ee7b7";
}

export function heatClass(value: number, max: number): string {
  if (max <= 0 || value <= 0) return "bg-slate-200";
  const pct = value / max;
  if (pct > 0.75) return "bg-red-500 text-white";
  if (pct > 0.5) return "bg-orange-400 text-white";
  if (pct > 0.25) return "bg-amber-300";
  return "bg-emerald-200";
}

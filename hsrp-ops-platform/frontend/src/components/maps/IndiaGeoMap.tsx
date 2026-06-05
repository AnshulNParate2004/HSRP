import { useEffect, useMemo, useState } from "react";
import { ComposableMap, Geographies, Geography, ZoomableGroup } from "react-simple-maps";
import { Minus, Plus, RotateCcw } from "lucide-react";
import {
  buildValueLookup,
  heatFill,
  normalizeStateName,
  type StateMapDatum,
} from "./indiaGeoUtils";

type GeoFeature = {
  type: string;
  properties?: Record<string, unknown>;
  geometry: { type: string; coordinates: unknown };
};

const INDIA_GEO_URL = "/data/india-states.geojson";

const MAP_CENTER: [number, number] = [82, 23];
const MAP_PROJECTION = {
  center: MAP_CENTER,
  scale: 950,
};

interface IndiaGeoMapProps {
  data: StateMapDatum[];
}

export function IndiaGeoMap({ data }: IndiaGeoMapProps) {
  const [hovered, setHovered] = useState<string | null>(null);
  const [features, setFeatures] = useState<GeoFeature[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [zoom, setZoom] = useState(1);

  const lookup = useMemo(() => buildValueLookup(data), [data]);
  const max = useMemo(() => Math.max(...data.map((d) => d.value), 1), [data]);

  const hoveredDatum = hovered ? lookup.get(normalizeStateName(hovered)) : undefined;

  useEffect(() => {
    let cancelled = false;

    fetch(INDIA_GEO_URL)
      .then((res) => {
        if (!res.ok) throw new Error(`Map data not found (${res.status})`);
        return res.json() as Promise<{ features?: GeoFeature[] }>;
      })
      .then((collection) => {
        if (!cancelled) {
          setFeatures(collection.features ?? []);
          setLoadError(null);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setFeatures([]);
          setLoadError(err instanceof Error ? err.message : "Failed to load map data");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (loadError) {
    return (
      <div className="flex h-[360px] items-center justify-center rounded-lg border border-dashed border-black/20 bg-muted/30 text-sm text-muted-foreground">
        Map unavailable: {loadError}
      </div>
    );
  }

  if (!features) {
    return (
      <div className="flex h-[360px] items-center justify-center rounded-lg border border-dashed border-black/20 bg-muted/20 text-sm text-muted-foreground">
        Loading map…
      </div>
    );
  }

  return (
    <div className="relative w-full">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <p className="text-[10px] text-muted-foreground">
          Drag to pan · Scroll to zoom
        </p>
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => setZoom((z) => Math.max(0.8, +(z - 0.35).toFixed(2)))}
            className="h-7 w-7 flex items-center justify-center rounded-md border border-black/20 bg-card hover:bg-muted"
            title="Zoom out"
          >
            <Minus className="h-3.5 w-3.5" />
          </button>
          <span className="text-[10px] font-medium text-muted-foreground w-10 text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            type="button"
            onClick={() => setZoom((z) => Math.min(4, +(z + 0.35).toFixed(2)))}
            className="h-7 w-7 flex items-center justify-center rounded-md border border-black/20 bg-card hover:bg-muted"
            title="Zoom in"
          >
            <Plus className="h-3.5 w-3.5" />
          </button>
          <button
            type="button"
            onClick={() => setZoom(1)}
            className="h-7 w-7 flex items-center justify-center rounded-md border border-black/20 bg-card hover:bg-muted"
            title="Reset view"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      <div className="max-h-[420px] overflow-auto rounded-lg border border-black/10 bg-slate-50/40 touch-pan-x touch-pan-y">
        <ComposableMap
          projection="geoMercator"
          projectionConfig={MAP_PROJECTION}
          width={800}
          height={520}
          className="w-full min-w-[640px] h-auto"
        >
          <ZoomableGroup
            center={MAP_CENTER}
            zoom={zoom}
            minZoom={0.6}
            maxZoom={4}
            onMoveEnd={({ zoom: nextZoom }) => setZoom(nextZoom)}
            filterZoomEvent={(event) => {
              if (event.type === "wheel") return true;
              if (event.type === "mousedown" || event.type === "touchstart") return true;
              return false;
            }}
          >
            <Geographies geography={features}>
              {({ geographies }) =>
                geographies.map((geo) => {
                  const stateName = String(geo.properties?.ST_NM ?? "");
                  const datum = lookup.get(normalizeStateName(stateName));
                  const value = datum?.value ?? 0;
                  const isHovered = hovered === stateName;

                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      fill={isHovered ? "#6366f1" : heatFill(value, max)}
                      stroke="#334155"
                      strokeWidth={0.35}
                      style={{
                        default: { outline: "none", transition: "fill 150ms ease" },
                        hover: { outline: "none", cursor: "pointer" },
                        pressed: { outline: "none" },
                      }}
                      onMouseEnter={() => setHovered(stateName)}
                      onMouseLeave={() => setHovered(null)}
                    />
                  );
                })
              }
            </Geographies>
          </ZoomableGroup>
        </ComposableMap>
      </div>

      {hovered && (
        <div className="absolute top-12 left-3 rounded-lg border-2 border-black/20 bg-card/95 backdrop-blur px-3 py-2 shadow-sm pointer-events-none z-10">
          <p className="text-xs font-semibold">{hovered}</p>
          <p className="text-sm font-bold">
            {hoveredDatum ? (hoveredDatum.label ?? hoveredDatum.value) : "No activity"}
          </p>
        </div>
      )}
    </div>
  );
}

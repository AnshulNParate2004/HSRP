import { useMemo, useState } from "react";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import {
  buildValueLookup,
  heatFill,
  normalizeStateName,
  type StateMapDatum,
} from "./indiaGeoUtils";

const INDIA_GEO_URL = "/data/india-states.geojson";

const MAP_PROJECTION = {
  center: [82, 23] as [number, number],
  scale: 950,
};

interface IndiaGeoMapProps {
  data: StateMapDatum[];
}

export function IndiaGeoMap({ data }: IndiaGeoMapProps) {
  const [hovered, setHovered] = useState<string | null>(null);
  const lookup = useMemo(() => buildValueLookup(data), [data]);
  const max = useMemo(() => Math.max(...data.map((d) => d.value), 1), [data]);

  const hoveredDatum = hovered ? lookup.get(normalizeStateName(hovered)) : undefined;

  return (
    <div className="relative w-full">
      <ComposableMap
        projection="geoMercator"
        projectionConfig={MAP_PROJECTION}
        width={800}
        height={520}
        className="w-full h-auto"
      >
        <Geographies geography={INDIA_GEO_URL}>
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
      </ComposableMap>

      {hovered && (
        <div className="absolute top-3 left-3 rounded-lg border-2 border-black/20 bg-card/95 backdrop-blur px-3 py-2 shadow-sm pointer-events-none">
          <p className="text-xs font-semibold">{hovered}</p>
          <p className="text-sm font-bold">
            {hoveredDatum ? (hoveredDatum.label ?? hoveredDatum.value) : "No activity"}
          </p>
        </div>
      )}
    </div>
  );
}

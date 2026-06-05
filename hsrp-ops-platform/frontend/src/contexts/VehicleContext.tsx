import { createContext, useContext, useState, type ReactNode } from "react";
import type { VehicleFilter } from "@/types";

interface VehicleContextType {
  vehicleFilter: VehicleFilter;
  setVehicleFilter: (v: VehicleFilter) => void;
  apiVehicleType: string | null;
}

const VehicleContext = createContext<VehicleContextType | undefined>(undefined);

export function VehicleProvider({ children }: { children: ReactNode }) {
  const [vehicleFilter, setVehicleFilter] = useState<VehicleFilter>("all");
  const apiVehicleType = vehicleFilter === "all" ? null : vehicleFilter;

  return (
    <VehicleContext.Provider value={{ vehicleFilter, setVehicleFilter, apiVehicleType }}>
      {children}
    </VehicleContext.Provider>
  );
}

export function useVehicleFilter() {
  const ctx = useContext(VehicleContext);
  if (!ctx) throw new Error("useVehicleFilter must be used within VehicleProvider");
  return ctx;
}

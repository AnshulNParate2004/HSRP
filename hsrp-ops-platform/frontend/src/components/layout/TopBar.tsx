import { Bell, LogOut, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import { useVehicleFilter } from "@/contexts/VehicleContext";
import { useAuth } from "@/contexts/AuthContext";
import { useAppConfig } from "@/hooks/useAppConfig";
import type { VehicleFilter } from "@/types";

export function TopBar() {
  const { vehicleFilter, setVehicleFilter } = useVehicleFilter();
  const { user, logout } = useAuth();
  const { data: config } = useAppConfig();

  const options =
    config?.vehicle_filters?.length
      ? config.vehicle_filters
      : [
          { value: "all", label: "All Vehicles" },
          { value: "new", label: "New Vehicle" },
          { value: "old", label: "Old Vehicle" },
        ];

  return (
    <header className="sticky top-0 z-30 h-14 flex items-center justify-between border-b-2 border-black bg-card/90 backdrop-blur-sm px-5 shrink-0">
      <div className="flex items-center gap-2 pl-12 lg:pl-0">
        <Sparkles className="h-4 w-4 text-primary hidden sm:block" />
        <span className="text-sm font-semibold text-muted-foreground hidden sm:block">
          {config?.app?.description ?? "HSRP Operations Intelligence"}
        </span>
        {config?.llm_configured && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium hidden md:inline">
            AI: {config.llm_model}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <div className="flex bg-muted rounded-lg p-0.5 border border-black/30 h-8">
          {options.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setVehicleFilter(opt.value as VehicleFilter)}
              className={`px-2.5 py-0.5 text-[11px] font-medium rounded-md transition-colors whitespace-nowrap ${
                vehicleFilter === opt.value
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <Link
          to="/app/alerts"
          className="relative h-8 w-8 flex items-center justify-center rounded-lg hover:bg-muted text-muted-foreground border border-black/30"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 bg-destructive rounded-full" />
        </Link>

        {user && (
          <div className="hidden sm:flex items-center gap-2 pl-2 border-l border-black/20">
            <span className="text-[11px] text-muted-foreground max-w-[120px] truncate">{user.full_name}</span>
            <button
              onClick={logout}
              className="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-muted border border-black/30"
              title="Sign out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
}

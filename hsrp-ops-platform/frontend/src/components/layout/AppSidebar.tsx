import { NavLink, useLocation } from "react-router-dom";
import { ChevronLeft, Shield } from "lucide-react";
import { cn } from "@/lib/utils";
import { useSidebar } from "@/contexts/SidebarContext";
import { useAppConfig } from "@/hooks/useAppConfig";
import { getNavIcon } from "@/lib/navIcons";
import { APP_NAME } from "@/lib/branding";

export function AppSidebar() {
  const { collapsed, setCollapsed } = useSidebar();
  const location = useLocation();
  const { data: config } = useAppConfig();

  const navItems = config?.navigation ?? [];

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 flex h-screen flex-col bg-card border-r-2 border-black transition-all duration-200 hidden lg:flex",
        collapsed ? "w-[68px]" : "w-60"
      )}
    >
      <button
        onClick={() => setCollapsed(!collapsed)}
        className={cn(
          "h-14 flex items-center border-b-2 border-black shrink-0 w-full text-left hover:bg-muted/40 transition-colors",
          collapsed ? "justify-center px-0" : "gap-2.5 px-4"
        )}
      >
        <div className="flex h-8 w-8 shrink-0 items-center justify-center bg-[#1d4ed8] rounded-lg border border-black/10">
          <Shield className="h-4 w-4 text-white" />
        </div>
        {!collapsed && (
          <div className="flex flex-col leading-none">
            <span className="text-sm font-bold text-foreground tracking-tight">
              {config?.app?.name ?? APP_NAME}
            </span>
            <span className="text-[10px] font-semibold text-accent tracking-wider uppercase">
              {config?.app?.tagline ?? "HSRP Ops"}
            </span>
          </div>
        )}
        {!collapsed && <ChevronLeft className="ml-auto h-3.5 w-3.5 text-muted-foreground" />}
      </button>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = getNavIcon(item.icon);
          const isActive =
            location.pathname === item.path ||
            (item.path !== "/app" && location.pathname.startsWith(item.path));

          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/app"}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 text-[13px] font-medium rounded-lg transition-all border-2 border-transparent",
                collapsed && "justify-center px-0",
                isActive
                  ? "bg-primary text-primary-foreground border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              )}
            >
              <Icon className="h-[18px] w-[18px] shrink-0" />
              {!collapsed && <span>{item.title}</span>}
            </NavLink>
          );
        })}
      </nav>

      <div className="border-t-2 border-black px-4 py-3">
        {!collapsed ? (
          <div className="flex items-center gap-2">
            <div className="h-1.5 w-1.5 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-[11px] text-muted-foreground">PAN India monitoring</span>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="h-1.5 w-1.5 bg-emerald-500 rounded-full animate-pulse" />
          </div>
        )}
      </div>
    </aside>
  );
}

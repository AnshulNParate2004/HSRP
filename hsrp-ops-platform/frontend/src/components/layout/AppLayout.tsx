import { Outlet } from "react-router-dom";
import { AppSidebar } from "./AppSidebar";
import { MobileSidebar } from "./MobileSidebar";
import { TopBar } from "./TopBar";
import { SidebarProvider, useSidebar } from "@/contexts/SidebarContext";

function AppLayoutInner() {
  const { collapsed } = useSidebar();
  return (
    <div className="flex min-h-screen w-full bg-background">
      <AppSidebar />
      <MobileSidebar />
      <div
        className={`flex flex-1 flex-col min-w-0 transition-all duration-200 ${collapsed ? "lg:ml-[68px]" : "lg:ml-60"}`}
      >
        <TopBar />
        <main className="flex-1 p-5 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export function AppLayout() {
  return (
    <SidebarProvider>
      <AppLayoutInner />
    </SidebarProvider>
  );
}

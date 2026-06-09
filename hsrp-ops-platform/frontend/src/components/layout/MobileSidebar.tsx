import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { Menu, X, Shield } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { useAppConfig } from "@/hooks/useAppConfig";
import { getNavIcon } from "@/lib/navIcons";
import { APP_NAME } from "@/lib/branding";

export function MobileSidebar() {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const { data: config } = useAppConfig();
  const navItems = config?.navigation ?? [];

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="lg:hidden fixed top-3 left-3 z-50 w-10 h-10 bg-primary text-primary-foreground rounded-xl flex items-center justify-center shadow-lg border-2 border-black"
        aria-label="Open menu"
      >
        <Menu size={20} />
      </button>

      <AnimatePresence>
        {open && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setOpen(false)}
              className="fixed inset-0 bg-foreground/20 backdrop-blur-sm z-40 lg:hidden"
            />
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              className="fixed left-0 top-0 h-full w-64 bg-card border-r-2 border-black z-50 lg:hidden flex flex-col"
            >
              <div className="h-14 flex items-center justify-between px-4 border-b-2 border-black">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center bg-[#1d4ed8] rounded-lg">
                    <Shield className="h-4 w-4 text-white" />
                  </div>
                  <span className="text-sm font-bold">{config?.app?.name ?? APP_NAME}</span>
                </div>
                <button onClick={() => setOpen(false)}>
                  <X className="h-5 w-5" />
                </button>
              </div>
              <nav className="flex-1 p-3 space-y-1">
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
                      onClick={() => setOpen(false)}
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg",
                        isActive ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted"
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      {item.title}
                    </NavLink>
                  );
                })}
              </nav>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}

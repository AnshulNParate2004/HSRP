import {
  LayoutDashboard,
  IndianRupee,
  Clock,
  Gauge,
  Package,
  Timer,
  Bell,
  Radio,
  MessageSquare,
  FileDown,
  TrendingUp,
  Plug,
  type LucideIcon,
} from "lucide-react";

const ICON_MAP: Record<string, LucideIcon> = {
  LayoutDashboard,
  IndianRupee,
  Clock,
  Gauge,
  Package,
  Timer,
  Bell,
  Radio,
  MessageSquare,
  FileDown,
  TrendingUp,
  Plug,
  BarChart3: LayoutDashboard,
};

export function getNavIcon(name: string): LucideIcon {
  return ICON_MAP[name] ?? LayoutDashboard;
}

import { motion } from "framer-motion";
import type { LucideIcon } from "lucide-react";

interface MetricItem {
  label: string;
  value: string | number;
  icon: LucideIcon;
  color: string;
  bg: string;
}

export function MetricCards({ metrics }: { metrics: MetricItem[] }) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
      {metrics.map((m, idx) => (
        <motion.div
          key={m.label}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.04 }}
          className="bg-card rounded-lg border-2 border-black/20 px-4 py-3 flex items-center gap-3 min-h-[72px]"
        >
          <div className={`w-9 h-9 rounded-lg shrink-0 ${m.bg} ${m.color} flex items-center justify-center`}>
            <m.icon className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide truncate">
              {m.label}
            </p>
            <p className="text-lg font-bold truncate">{m.value}</p>
          </div>
        </motion.div>
      ))}
    </div>
  );
}

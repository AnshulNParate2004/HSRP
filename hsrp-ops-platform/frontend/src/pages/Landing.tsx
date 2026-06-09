import { Link } from "react-router-dom";
import { Shield, ArrowRight, BarChart3, Clock, Package, Bell } from "lucide-react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { authApi } from "@/lib/api";
import { APP_NAME, COMPANY_NAME } from "@/lib/branding";

const FEATURE_ICONS: Record<string, typeof BarChart3> = {
  BarChart3,
  Clock,
  Package,
  Bell,
};

const DEFAULT_FEATURES = [
  { title: "Revenue Analytics", description: "State, OEM, and portal-wise contribution", icon: "BarChart3" },
  { title: "Pendency Monitor", description: "Real-time delay and SLA breach tracking", icon: "Clock" },
  { title: "Inventory Intelligence", description: "Stock shortage prediction and replenishment", icon: "Package" },
  { title: "AI Assistant", description: "Azure OpenAI powered operational Q&A", icon: "Bell" },
];

export default function Landing() {
  const { data: platform } = useQuery({
    queryKey: ["platform-info"],
    queryFn: authApi.platformInfo,
  });

  const features = DEFAULT_FEATURES;

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b-2 border-black bg-card">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center bg-[#1d4ed8] rounded-lg border border-black/10">
              <Shield className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm font-bold">{platform?.app?.name ?? APP_NAME}</p>
              <p className="text-[10px] text-muted-foreground uppercase tracking-wider">
                {platform?.app?.tagline ?? "HSRP Ops"}
              </p>
            </div>
          </div>
          <Link
            to="/login"
            className="px-4 py-2 text-sm font-semibold rounded-lg bg-primary text-primary-foreground border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
          >
            Sign in
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-16">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <p className="text-sm font-semibold text-primary uppercase tracking-wider mb-3">
            {platform?.app?.company ?? COMPANY_NAME}
          </p>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
            AI-Powered HSRP Operations & Analytics
          </h1>
          <p className="text-lg text-muted-foreground mb-8">
            Centralized, real-time visibility into the complete HSRP lifecycle across India — revenue,
            pendency, inventory, TAT, and Azure OpenAI assistant.
          </p>
          <Link
            to="/login"
            className="inline-flex items-center gap-2 px-6 py-3 text-base font-semibold rounded-xl bg-primary text-primary-foreground border-2 border-black shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:translate-y-0.5 transition-all"
          >
            Launch Operations Dashboard
            <ArrowRight className="h-5 w-5" />
          </Link>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map((f, i) => {
            const Icon = FEATURE_ICONS[f.icon] ?? BarChart3;
            return (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                className="rounded-xl border-2 border-black/20 bg-card p-5"
              >
                <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center mb-3">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="font-bold mb-1">{f.title}</h3>
                <p className="text-sm text-muted-foreground">{f.description}</p>
              </motion.div>
            );
          })}
        </div>
      </main>
    </div>
  );
}

import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { AuthProvider } from "@/contexts/AuthContext";
import { VehicleProvider } from "@/contexts/VehicleContext";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { PageLoader } from "@/components/ui/PageLoader";
import Landing from "@/pages/Landing";
import Login from "@/pages/Login";

const Dashboard = lazy(() => import("@/pages/Dashboard"));
const Revenue = lazy(() => import("@/pages/Revenue"));
const Pendency = lazy(() => import("@/pages/Pendency"));
const Performance = lazy(() => import("@/pages/Performance"));
const Inventory = lazy(() => import("@/pages/Inventory"));
const Tat = lazy(() => import("@/pages/Tat"));
const Alerts = lazy(() => import("@/pages/Alerts"));
const Monitoring = lazy(() => import("@/pages/Monitoring"));
const Assistant = lazy(() => import("@/pages/Assistant"));
const Reports = lazy(() => import("@/pages/Reports"));
const Planning = lazy(() => import("@/pages/Planning"));
const Integrations = lazy(() => import("@/pages/Integrations"));

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <VehicleProvider>
          <BrowserRouter>
            <Suspense fallback={<PageLoader />}>
              <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/login" element={<Login />} />
                <Route
                  path="/app"
                  element={
                    <ProtectedRoute>
                      <AppLayout />
                    </ProtectedRoute>
                  }
                >
                  <Route index element={<Dashboard />} />
                  <Route path="revenue" element={<Revenue />} />
                  <Route path="pendency" element={<Pendency />} />
                  <Route path="performance" element={<Performance />} />
                  <Route path="inventory" element={<Inventory />} />
                  <Route path="tat" element={<Tat />} />
                  <Route path="alerts" element={<Alerts />} />
                  <Route path="monitoring" element={<Monitoring />} />
                  <Route path="assistant" element={<Assistant />} />
                  <Route path="reports" element={<Reports />} />
                  <Route path="planning" element={<Planning />} />
                  <Route path="integrations" element={<Integrations />} />
                </Route>
              </Routes>
            </Suspense>
          </BrowserRouter>
        </VehicleProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

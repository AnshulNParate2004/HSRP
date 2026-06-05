import { useQuery } from "@tanstack/react-query";
import { configApi } from "@/lib/api";

export function useAppConfig() {
  return useQuery({
    queryKey: ["app-config"],
    queryFn: configApi.ui,
    staleTime: 5 * 60_000,
  });
}

export function useOrderStages() {
  const { data } = useAppConfig();
  const stages: Record<string, string> = {};
  for (const s of data?.order_stages ?? []) {
    stages[s.key] = s.label;
  }
  return stages;
}

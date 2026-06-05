import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Send, Sparkles, Loader2, Trash2, Bot, User } from "lucide-react";
import { assistantApi } from "@/lib/api";
import { useVehicleFilter } from "@/contexts/VehicleContext";
import { useAppConfig } from "@/hooks/useAppConfig";
import { PageHeader } from "@/components/ui/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AssistantAnswer } from "@/components/assistant/AssistantAnswer";

type ChatItem = {
  id: string;
  q: string;
  a?: string;
  sources?: string[];
  llm_used?: boolean;
  status: "loading" | "done" | "error";
  error?: string;
};

export default function AssistantPage() {
  const { apiVehicleType, vehicleFilter } = useVehicleFilter();
  const { data: config } = useAppConfig();
  const [question, setQuestion] = useState("");
  const [activeSuggestion, setActiveSuggestion] = useState<string | null>(null);
  const [history, setHistory] = useState<ChatItem[]>([]);

  const { data: suggestionsData } = useQuery({
    queryKey: ["assistant-suggestions", apiVehicleType],
    queryFn: () => assistantApi.suggestions(apiVehicleType),
  });

  const ask = useMutation({
    mutationFn: ({ question: q }: { question: string; id: string }) =>
      assistantApi.ask(q, apiVehicleType),
  });

  const submit = (q?: string) => {
    const text = (q ?? question).trim();
    if (!text || ask.isPending) return;

    const id = crypto.randomUUID();
    if (q) setActiveSuggestion(q);

    setHistory((h) => [{ id, q: text, status: "loading" }, ...h]);
    setQuestion("");

    ask.mutate(
      { question: text, id },
      {
        onSuccess: (res, vars) => {
          setHistory((h) =>
            h.map((item) =>
              item.id === vars.id
                ? {
                    ...item,
                    status: "done",
                    a: res.answer,
                    sources: res.sources,
                    llm_used: res.llm_used,
                  }
                : item
            )
          );
          setActiveSuggestion(null);
        },
        onError: (err, vars) => {
          setHistory((h) =>
            h.map((item) =>
              item.id === vars.id
                ? {
                    ...item,
                    status: "error",
                    error: err instanceof Error ? err.message : "Request failed",
                  }
                : item
            )
          );
          setActiveSuggestion(null);
        },
      }
    );
  };

  const contextLabel = useMemo(() => {
    if (vehicleFilter === "new") return "New Vehicle";
    if (vehicleFilter === "old") return "Old Vehicle";
    return "All Vehicles";
  }, [vehicleFilter]);

  const isLoading = history.some((item) => item.status === "loading");

  return (
    <div className="space-y-6 max-w-5xl">
      <PageHeader
        title="AI Operations Assistant"
        description={
          config?.llm_configured
            ? `Powered by Azure OpenAI (${config.llm_model}) — full answers appear when analysis completes`
            : "Configure AZURE_OPENAI_* in backend .env to enable LLM"
        }
      />

      <div className="grid lg:grid-cols-12 gap-4">
        <Card className="lg:col-span-8 border-2 border-primary/30">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between gap-3">
              <CardTitle className="text-sm">Conversation</CardTitle>
              <div className="text-[11px] rounded-full px-2.5 py-1 border border-black/10 bg-muted text-muted-foreground">
                Context: <span className="font-semibold text-foreground">{contextLabel}</span>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            {history.length === 0 ? (
              <div className="rounded-xl border border-dashed border-black/15 bg-muted/20 p-8 text-center">
                <Bot className="h-6 w-6 text-primary mx-auto mb-2" />
                <p className="text-sm font-medium">Ask your first operational question</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Answers load in full when ready — no streaming.
                </p>
              </div>
            ) : (
              <div className="space-y-4 max-h-[52vh] overflow-y-auto pr-1">
                {history.map((item) => (
                  <div key={item.id} className="space-y-2">
                    <div className="flex items-start gap-2 justify-end">
                      <div className="rounded-xl bg-muted/60 border border-black/10 px-3.5 py-2 text-sm max-w-[85%]">
                        {item.q}
                      </div>
                      <div className="h-7 w-7 rounded-full border border-black/15 bg-background flex items-center justify-center shrink-0">
                        <User className="h-4 w-4 text-muted-foreground" />
                      </div>
                    </div>

                    <div className="flex items-start gap-2">
                      <div className="h-7 w-7 rounded-full border border-primary/20 bg-primary/10 flex items-center justify-center shrink-0">
                        {item.status === "loading" ? (
                          <Loader2 className="h-4 w-4 text-primary animate-spin" />
                        ) : (
                          <Sparkles className="h-4 w-4 text-primary" />
                        )}
                      </div>
                      <div className="rounded-xl bg-card border-2 border-black/15 px-3.5 py-3 max-w-[90%] min-w-[200px]">
                        {item.status === "loading" && (
                          <div className="space-y-2">
                            <p className="text-sm text-muted-foreground">Analyzing live data…</p>
                            <div className="h-1.5 w-32 rounded-full bg-muted overflow-hidden">
                              <div className="h-full w-1/2 bg-primary/60 rounded-full animate-pulse" />
                            </div>
                          </div>
                        )}

                        {item.status === "error" && (
                          <p className="text-sm text-red-600">{item.error ?? "Something went wrong."}</p>
                        )}

                        {item.status === "done" && item.a && (
                          <>
                            <AssistantAnswer text={item.a} />
                            <p className="text-[10px] text-muted-foreground mt-3 pt-2 border-t border-black/5">
                              {item.llm_used ? "Azure OpenAI" : "Rule engine"}
                              {item.sources && item.sources.length > 0
                                ? ` · ${item.sources.length} tool${item.sources.length > 1 ? "s" : ""} used`
                                : ""}
                            </p>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="mt-4 pt-4 border-t border-black/10">
              <div className="flex gap-2">
                <input
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && submit()}
                  placeholder="Ask about revenue, pendency, inventory, ESO performance…"
                  disabled={isLoading}
                  className="flex-1 rounded-lg border-2 border-black/20 px-4 py-2.5 text-sm focus:outline-none focus:border-primary disabled:opacity-60"
                />
                <button
                  onClick={() => submit()}
                  disabled={isLoading || !question.trim()}
                  className="px-4 rounded-lg bg-primary text-primary-foreground border-2 border-black disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                </button>
              </div>
              {history.length > 0 && (
                <button
                  type="button"
                  onClick={() => setHistory([])}
                  disabled={isLoading}
                  className="mt-3 inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground disabled:opacity-50"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Clear chat
                </button>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-4">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Quick Prompts</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {(suggestionsData?.suggestions ?? []).map((s) => (
              <button
                key={s}
                onClick={() => submit(s)}
                disabled={isLoading}
                className="w-full text-left text-xs px-3 py-2 rounded-lg border border-black/10 bg-muted/40 hover:bg-primary/10 transition-colors disabled:opacity-60"
              >
                {ask.isPending && activeSuggestion === s ? (
                  <span className="inline-flex items-center gap-1.5">
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    Running...
                  </span>
                ) : (
                  s
                )}
              </button>
            ))}
            {!(suggestionsData?.suggestions ?? []).length && (
              <p className="text-xs text-muted-foreground">No suggestions yet. Ask a custom question.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

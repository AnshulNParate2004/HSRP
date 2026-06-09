import { useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import { Shield } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useQuery } from "@tanstack/react-query";
import { authApi } from "@/lib/api";
import { APP_NAME, DEMO_ADMIN_EMAIL } from "@/lib/branding";

export default function LoginPage() {
  const { login, user } = useAuth();
  const { data: platform } = useQuery({
    queryKey: ["platform-info"],
    queryFn: authApi.platformInfo,
  });
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname ?? "/app";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (user) return <Navigate to={from} replace />;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email.trim(), password);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "";
      if (msg.includes("at least 8 characters") || msg.includes("string_too_short")) {
        setError("Password must be at least 8 characters. Try: Admin@123");
      } else if (msg.includes("401") || msg.toLowerCase().includes("invalid")) {
        setError("Invalid email or password.");
      } else if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
        setError("Cannot reach server. Start backend: npm run dev");
      } else {
        setError(`Sign-in failed. Use ${DEMO_ADMIN_EMAIL} / Admin@123`);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-6">
      <div className="w-full max-w-md rounded-xl border-2 border-black bg-card p-8 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <div className="flex items-center gap-3 mb-6">
          <div className="flex h-10 w-10 items-center justify-center bg-[#1d4ed8] rounded-lg">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold">{platform?.app?.name ?? APP_NAME}</h1>
            <p className="text-xs text-muted-foreground">Secure sign-in</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-medium uppercase text-muted-foreground">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border-2 border-black/20 px-3 py-2 text-sm"
              autoComplete="username"
            />
          </div>
          <div>
            <label className="text-xs font-medium uppercase text-muted-foreground">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border-2 border-black/20 px-3 py-2 text-sm"
              autoComplete="current-password"
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold border-2 border-black disabled:opacity-60"
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="mt-3 text-center text-[11px] text-muted-foreground bg-muted/50 rounded-lg p-2">
          Default login (copy both):<br />
          <span className="font-mono">{DEMO_ADMIN_EMAIL}</span>
          <br />
          <span className="font-mono">Admin@123</span>
          <span className="block mt-1 text-[10px]">Password must be 8+ characters</span>
        </p>

        <p className="mt-4 text-center text-xs text-muted-foreground">
          <Link to="/" className="underline">Back to home</Link>
        </p>
      </div>
    </div>
  );
}

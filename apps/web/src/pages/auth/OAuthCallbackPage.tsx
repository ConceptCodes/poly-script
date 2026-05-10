import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { apiFetch } from "../../lib/api";
import { finishGoogleOAuthFlow } from "../../lib/oauth";
import { type Team, type User, useAppStore } from "../../lib/store";

export function OAuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { initializeFromAuth } = useAppStore();
  const [message, setMessage] = useState("Completing sign in...");

  useEffect(() => {
    let cancelled = false;

    const completeOAuth = async () => {
      try {
        const tokens = await finishGoogleOAuthFlow(searchParams);
        localStorage.setItem("access_token", tokens.access_token);
        localStorage.setItem("refresh_token", tokens.refresh_token);

        const meData = await apiFetch<{ user: User; team: Team | null }>("/auth/me");
        initializeFromAuth(meData.user, meData.team);

        if (!cancelled) {
          navigate(meData.team ? "/dashboard" : "/onboarding", { replace: true });
        }
      } catch (err) {
        console.error("OAuth callback failed:", err);
        if (!cancelled) {
          setMessage("Unable to complete Google sign in.");
          navigate("/login", { replace: true });
        }
      }
    };

    void completeOAuth();

    return () => {
      cancelled = true;
    };
  }, [initializeFromAuth, navigate, searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="rounded-2xl border border-border bg-card p-8 shadow-lg text-center space-y-4">
        <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        <p className="text-sm text-muted-foreground">{message}</p>
      </div>
    </div>
  );
}

import { Toaster } from "@poly/ui/toaster";
import { QueryClientProvider } from "@tanstack/react-query";
import { useEffect } from "react";
import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { apiFetch } from "./lib/api";
import { queryClient } from "./lib/queryClient";
import { useAppStore } from "./lib/store";
import { ForgotPasswordPage } from "./pages/auth/ForgotPasswordPage";
import { LoginPage } from "./pages/auth/LoginPage";
import { OAuthCallbackPage } from "./pages/auth/OAuthCallbackPage";
import { ResetPasswordPage } from "./pages/auth/ResetPasswordPage";
import { SignupPage } from "./pages/auth/SignupPage";
import { VerifyEmailCodePage } from "./pages/auth/VerifyEmailCodePage";
import { VerifyEmailPage } from "./pages/auth/VerifyEmailPage";
import { BillingPage } from "./pages/billing/index";
import { CheckoutCancelPage } from "./pages/checkout/CheckoutCancelPage";
import { CheckoutSuccessPage } from "./pages/checkout/CheckoutSuccessPage";
import { DashboardPage } from "./pages/dashboard/DashboardPage";
import { ForbiddenPage } from "./pages/errors/ForbiddenPage";
import { InternalServerErrorPage } from "./pages/errors/InternalServerErrorPage";
import { NotFoundPage } from "./pages/errors/NotFoundPage";
import { SessionExpiredPage } from "./pages/errors/SessionExpiredPage";
import { JobsPage } from "./pages/jobs";
import { LiveTranscriptViewerPage } from "./pages/jobs/[jobId]/live";
import { CompletedJobsPage } from "./pages/jobs/completed";
import { PendingJobsPage } from "./pages/jobs/pending";
import { LibraryPage } from "./pages/library/index";
import { OnboardingPage } from "./pages/onboarding/OnboardingPage";
import { TeamSettingsPage } from "./pages/settings/TeamSettingsPage";
import { UserSettingsPage } from "./pages/settings/UserSettingsPage";
import { TranscriptEditorPage } from "./pages/transcripts/[id]/index";
import UploadPage from "./pages/upload/index";

function AuthBootstrap() {
  const { initializeFromAuth, setAuth } = useAppStore();

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setAuth({ isLoading: false });
        return;
      }

      try {
        const data = await apiFetch<{
          user: {
            id: string;
            email: string;
            full_name: string;
            is_verified: boolean;
            is_active: boolean;
            is_suspended: boolean;
            created_at: string;
          };
          team: {
            id: string;
            name: string;
            default_language: string;
            created_at: string;
            plan: string;
          } | null;
        }>("/auth/me");

        initializeFromAuth(
          {
            id: String(data.user.id),
            email: data.user.email,
            name: data.user.full_name,
            verified: data.user.is_verified,
            createdAt: data.user.created_at,
            host_language: "en",
            theme: "system",
            notifications: {
              email: true,
              job_completion: true,
              in_app: true,
            },
          },
          data.team
            ? {
                id: data.team.id,
                name: data.team.name,
                defaultLanguage: data.team.default_language,
                createdAt: data.team.created_at,
              }
            : null,
        );
      } catch (err: unknown) {
        const apiError = err as { status?: number };
        if (apiError.status === 401) {
          // Token expired or invalid — clear stored tokens
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
        setAuth({ isLoading: false });
      }
    };

    initAuth();
  }, [initializeFromAuth, setAuth]);

  return null;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-background text-foreground">
          <AuthBootstrap />
          <main>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />

              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />
              <Route path="/verify-email" element={<VerifyEmailPage />} />
              <Route path="/verify-email-code" element={<VerifyEmailCodePage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />
              <Route path="/auth/oauth/callback" element={<OAuthCallbackPage />} />

              <Route path="/onboarding" element={<OnboardingPage />} />

              <Route path="/checkout/success" element={<CheckoutSuccessPage />} />
              <Route path="/checkout/cancel" element={<CheckoutCancelPage />} />

              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/settings/team"
                element={
                  <ProtectedRoute>
                    <TeamSettingsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/settings/user"
                element={
                  <ProtectedRoute>
                    <UserSettingsPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/upload"
                element={
                  <ProtectedRoute>
                    <UploadPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/library"
                element={
                  <ProtectedRoute>
                    <LibraryPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/transcripts/:id"
                element={
                  <ProtectedRoute>
                    <TranscriptEditorPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/billing"
                element={
                  <ProtectedRoute>
                    <BillingPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/jobs"
                element={
                  <ProtectedRoute>
                    <JobsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/jobs/pending"
                element={
                  <ProtectedRoute>
                    <PendingJobsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/jobs/completed"
                element={
                  <ProtectedRoute>
                    <CompletedJobsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/jobs/:jobId/live"
                element={
                  <ProtectedRoute>
                    <LiveTranscriptViewerPage />
                  </ProtectedRoute>
                }
              />

              <Route path="/404" element={<NotFoundPage />} />
              <Route path="/403" element={<ForbiddenPage />} />
              <Route path="/500" element={<InternalServerErrorPage />} />
              <Route path="/session-expired" element={<SessionExpiredPage />} />

              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </main>
        </div>
      </Router>
      <Toaster />
    </QueryClientProvider>
  );
}

export default App;

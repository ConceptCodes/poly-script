import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import "./App.css";

import { Toaster } from "@poly/ui/toaster";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { queryClient } from "./lib/queryClient";
import { ForgotPasswordPage } from "./pages/auth/ForgotPasswordPage";
import { LoginPage } from "./pages/auth/LoginPage";
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
import { OnboardingPage } from "./pages/onboarding/OnboardingPage";
import { TeamSettingsPage } from "./pages/settings/TeamSettingsPage";
import { UserSettingsPage } from "./pages/settings/UserSettingsPage";
import UploadPage from "./pages/upload/index";

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-background text-foreground">
          <main>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />

              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />
              <Route path="/verify-email" element={<VerifyEmailPage />} />
              <Route path="/verify-email-code" element={<VerifyEmailCodePage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />

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
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;

import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import "./App.css";

import { LoginPage } from "./pages/auth/LoginPage";
import { SignupPage } from "./pages/auth/SignupPage";
import { VerifyEmailPage } from "./pages/auth/VerifyEmailPage";
import { ForgotPasswordPage } from "./pages/auth/ForgotPasswordPage";
import { ResetPasswordPage } from "./pages/auth/ResetPasswordPage";

import { OnboardingPage } from "./pages/onboarding/OnboardingPage";

import { DashboardPage } from "./pages/dashboard/DashboardPage";
import { TeamSettingsPage } from "./pages/settings/TeamSettingsPage";
import { UserSettingsPage } from "./pages/settings/UserSettingsPage";

import { BillingPage } from "./pages/billing/index";
import { UploadPage } from "./pages/upload/index";

import { NotFoundPage } from "./pages/errors/NotFoundPage";
import { ForbiddenPage } from "./pages/errors/ForbiddenPage";
import { InternalServerErrorPage } from "./pages/errors/InternalServerErrorPage";
import { SessionExpiredPage } from "./pages/errors/SessionExpiredPage";

import { ProtectedRoute } from "./components/ProtectedRoute";
import { queryClient } from "./lib/queryClient";

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
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />

              <Route path="/onboarding" element={<OnboardingPage />} />

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

              <Route path="/404" element={<NotFoundPage />} />
              <Route path="/403" element={<ForbiddenPage />} />
              <Route path="/500" element={<InternalServerErrorPage />} />
              <Route path="/session-expired" element={<SessionExpiredPage />} />

              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </main>
        </div>
      </Router>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;

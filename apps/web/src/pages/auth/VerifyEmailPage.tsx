import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useSearchParams, useNavigate } from "react-router-dom";
import { Button } from "@poly/ui";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@poly/ui";
import { Alert, AlertDescription } from "@poly/ui";
import { apiFetch } from "../../lib/api";

type VerificationStatus = "pending" | "success" | "failed";

export function VerifyEmailPage() {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<VerificationStatus>(token ? "pending" : "failed");
  const [error, setError] = useState<string | null>(null);
  const [resending, setResending] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);
  const pendingEmail = localStorage.getItem("pending_email") || "";

  useEffect(() => {
    if (token) {
      verifyEmail(token);
    }
  }, [token]);

  const verifyEmail = async (verificationToken: string) => {
    try {
      await apiFetch("/auth/verify-email", {
        method: "POST",
        body: { token: verificationToken },
      });
      setStatus("success");
    } catch (err: any) {
      setStatus("failed");
      setError(err.message || t("auth.verifyEmail.failed.resendError"));
    }
  };

  const resendVerification = async () => {
    setResending(true);
    setResendSuccess(false);
    try {
      await apiFetch("/auth/resend-verification", {
        method: "POST",
        body: { email: pendingEmail },
      });
      setResendSuccess(true);
    } catch (err: any) {
      setError(err.message || t("auth.verifyEmail.failed.resendError"));
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-center">
            {status === "success"
              ? t("auth.verifyEmail.success.title")
              : t("auth.verifyEmail.pending.title")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {status === "pending" && (
            <div className="text-center space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
              <p className="text-sm text-gray-600">{t("auth.verifyEmail.pending.subtitle")}</p>
            </div>
          )}

          {status === "success" && (
            <div className="space-y-4">
              <Alert>
                <AlertDescription className="text-center">
                  {t("auth.verifyEmail.success.subtitle")}
                </AlertDescription>
              </Alert>
              <p className="text-sm text-center text-gray-600">
                {t("auth.verifyEmail.success.subtitle")}
              </p>
              <Button onClick={() => navigate("/auth/login")} className="w-full">
                {t("auth.verifyEmail.success.login")}
              </Button>
            </div>
          )}

          {status === "failed" && (
            <div className="space-y-4">
              <Alert variant="destructive">
                <AlertDescription>
                  {error || t("auth.verifyEmail.failed.subtitle")}
                </AlertDescription>
              </Alert>
              {token && (
                <>
                  <p className="text-sm text-center text-gray-600">
                    {t("auth.verifyEmail.failed.subtitle")}
                  </p>
                  <Button
                    onClick={resendVerification}
                    variant="outline"
                    className="w-full"
                    disabled={resending}
                  >
                    {resending
                      ? t("auth.verifyEmail.failed.sending")
                      : t("auth.verifyEmail.failed.resend")}
                  </Button>
                  {resendSuccess && (
                    <p className="text-sm text-center text-green-600">
                      {t("auth.verifyEmail.failed.resendSuccess")}
                    </p>
                  )}
                </>
              )}
              <div className="pt-4">
                <Button onClick={() => navigate("/auth/login")} variant="ghost" className="w-full">
                  {t("auth.verifyEmail.success.login")}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

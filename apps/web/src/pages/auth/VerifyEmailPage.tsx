import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "@poly/ui/components/ui/button";
import { Alert, AlertDescription } from "@poly/ui/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/components/ui/card";
import { api } from "@/lib/api";

type VerificationStatus = "pending" | "success" | "failed";

export default function VerifyEmailPage() {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<VerificationStatus>(token ? "pending" : "failed");
  const [error, setError] = useState<string | null>(null);
  const [resending, setResending] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);

  useState(() => {
    if (token) {
      verifyEmail(token);
    }
  });

  const verifyEmail = async (verificationToken: string) => {
    try {
      await api.post("/v1/auth/verify-email", { token: verificationToken });
      setStatus("success");
    } catch (err: any) {
      setStatus("failed");
      setError(err.response?.data?.error?.message || t("error.something_went_wrong"));
    }
  };

  const resendVerification = async () => {
    setResending(true);
    setResendSuccess(false);
    try {
      await api.post("/v1/auth/resend-verification", { token });
      setResendSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || t("error.something_went_wrong"));
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-center">
            {status === "success" ? t("auth.email_verified") : t("auth.verify_email")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {status === "pending" && (
            <div className="text-center space-y-4">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
              <p className="text-sm text-gray-600">{t("auth.verifying_email")}</p>
            </div>
          )}

          {status === "success" && (
            <div className="space-y-4">
              <Alert>
                <AlertDescription className="text-center">
                  {t("auth.email_verified_success")}
                </AlertDescription>
              </Alert>
              <p className="text-sm text-center text-gray-600">{t("auth.can_now_login")}</p>
              <Button onClick={() => navigate("/auth/login")} className="w-full">
                {t("auth.go_to_login")}
              </Button>
            </div>
          )}

          {status === "failed" && (
            <div className="space-y-4">
              <Alert variant="destructive">
                <AlertDescription>{error || t("auth.verification_failed")}</AlertDescription>
              </Alert>
              {token && (
                <>
                  <p className="text-sm text-center text-gray-600">
                    {t("auth.resend_verification_instructions")}
                  </p>
                  <Button
                    onClick={resendVerification}
                    variant="outline"
                    className="w-full"
                    disabled={resending}
                  >
                    {resending ? t("common.sending") : t("auth.resend_verification")}
                  </Button>
                  {resendSuccess && (
                    <p className="text-sm text-center text-green-600">
                      {t("auth.verification_email_sent")}
                    </p>
                  )}
                </>
              )}
              <div className="pt-4">
                <Button onClick={() => navigate("/auth/login")} variant="ghost" className="w-full">
                  {t("common.back_to_login")}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

import {
  Alert,
  AlertDescription,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Label,
  useToast,
} from "@poly/ui";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../../lib/api";

export function VerifyEmailCodePage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [resending, setResending] = useState(false);
  const pendingEmail = localStorage.getItem("pending_email") || "";
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await apiFetch("/auth/verify-email-code", {
        method: "POST",
        body: { code },
      });
      setSuccess(true);
      setTimeout(() => {
        navigate("/onboarding");
      }, 2000);
    } catch (err: unknown) {
      const message =
        err instanceof Error && err.message ? err.message : "Invalid verification code";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResending(true);
    setError(null);

    try {
      await apiFetch("/auth/resend-verification", {
        method: "POST",
        body: { email: pendingEmail },
      });
      // Show success message
      toast({
        title: "Code resent",
        description: "A new verification code has been sent to your email.",
      });
    } catch (err: unknown) {
      const message = err instanceof Error && err.message ? err.message : "Failed to resend code";
      setError(message);
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-center">{t("auth.verifyEmailCode.title")}</CardTitle>
          <CardDescription className="text-center">
            {t("auth.verifyEmailCode.subtitle", { email: pendingEmail })}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {success ? (
            <div className="text-center space-y-4">
              <div className="text-success text-6xl">✓</div>
              <p className="text-lg font-medium">Email verified!</p>
              <p className="text-sm text-muted-foreground">Redirecting to onboarding...</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="code">Verification Code</Label>
                <Input
                  id="code"
                  type="text"
                  placeholder="123456"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  maxLength={6}
                  className="text-center text-2xl tracking-widest"
                />
                <p className="text-xs text-muted-foreground/70 text-center">
                  Enter the 6-digit code sent to your email
                </p>
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button type="submit" className="w-full" disabled={loading || code.length !== 6}>
                {loading ? "Verifying…" : "Verify Email"}
              </Button>

              <div className="text-center">
                <p className="text-sm text-muted-foreground">Didn't receive the code?</p>
                <Button
                  type="button"
                  variant="link"
                  onClick={handleResend}
                  disabled={resending}
                  className="text-sm"
                >
                  {resending ? "Sending…" : "Resend Code"}
                </Button>
              </div>

              <Button
                type="button"
                variant="ghost"
                onClick={() => navigate("/login")}
                className="w-full"
              >
                Back to Login
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

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
} from "@poly/ui";
import { useForm } from "@tanstack/react-form";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";
import { apiFetch } from "../../lib/api";
import { type Team, type User, useAppStore } from "../../lib/store";
import { createLoginSchema } from "./schemas";

export function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { initializeFromAuth } = useAppStore();
  const [error, setError] = useState<string | null>(null);

  const loginSchema = createLoginSchema(t);

  const form = useForm({
    defaultValues: {
      email: "",
      password: "",
    },
    validators: {
      onChange: loginSchema,
    },
    onSubmit: async ({ value }) => {
      setError(null);
      try {
        const data = await apiFetch<{
          access_token: string;
          refresh_token: string;
        }>("/auth/login", {
          method: "POST",
          body: value,
        });

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);

        // Fetch user details
        const meData = await apiFetch<{ user: User; team: Team | null }>("/auth/me");

        initializeFromAuth(meData.user, meData.team);

        // Check if onboarding is needed, or go to dashboard
        if (!meData.team) {
          navigate("/onboarding");
        } else {
          navigate("/dashboard");
        }
      } catch (err: unknown) {
        const apiError = err as {
          code?: string;
          status?: number;
          message?: string;
          detail?: string;
        };
        if (apiError.code === "ACCOUNT_SUSPENDED") {
          setError(t("auth.login.errors.suspended"));
        } else if (apiError.code === "EMAIL_NOT_VERIFIED") {
          setError(t("auth.login.errors.unverified"));
        } else if (apiError.status === 401) {
          setError(t("auth.login.errors.invalidCredentials"));
        } else {
          setError(apiError.message || apiError.detail || t("auth.login.error"));
        }
      }
    },
  });

  const handleGoogleLogin = () => {
    window.location.href = `${import.meta.env.VITE_API_URL || "http://localhost:8000/v1"}/auth/oauth/google`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl text-center font-bold">{t("auth.login.title")}</CardTitle>
          <CardDescription className="text-center">{t("auth.login.subtitle")}</CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault();
              e.stopPropagation();
              form.handleSubmit();
            }}
            className="space-y-4"
          >
            <form.Field
              name="email"
              validators={{
                onChange: ({ value }) => {
                  const result = loginSchema.shape.email.safeParse(value);
                  return result.success ? undefined : result.error.issues[0].message;
                },
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor="email">{t("auth.login.emailLabel")}</Label>
                  <Input
                    id="email"
                    placeholder={t("auth.login.emailPlaceholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    autoComplete="username"
                    spellCheck={false}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-sm text-destructive">
                      {field.state.meta.errors[0] as string}
                    </p>
                  )}
                </div>
              )}
            </form.Field>

            <form.Field
              name="password"
              validators={{
                onChange: ({ value }) => {
                  const result = loginSchema.shape.password.safeParse(value);
                  return result.success ? undefined : result.error.issues[0].message;
                },
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="password">{t("auth.login.passwordLabel")}</Label>
                    <Link
                      to="/auth/forgot-password"
                      className="text-sm text-primary hover:underline"
                    >
                      {t("auth.login.forgotPassword")}
                    </Link>
                  </div>
                  <Input
                    id="password"
                    type="password"
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    autoComplete="current-password"
                    spellCheck={false}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-sm text-destructive">
                      {field.state.meta.errors[0] as string}
                    </p>
                  )}
                </div>
              )}
            </form.Field>

            <Button type="submit" className="w-full" disabled={form.state.isSubmitting}>
              {form.state.isSubmitting ? t("common.loading") : t("auth.login.submit")}
            </Button>
          </form>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                {t("auth.login.continueWith")}
              </span>
            </div>
          </div>

          <Button variant="outline" type="button" className="w-full" onClick={handleGoogleLogin}>
            <svg
              className="mr-2 h-4 w-4"
              aria-hidden="true"
              focusable="false"
              data-prefix="fab"
              data-icon="google"
              role="img"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 488 512"
            >
              <path
                fill="currentColor"
                d="M488 261.8C488 403.3 391.1 504 248 504 110.8 504 0 393.2 0 256S110.8 8 248 8c66.8 0 123 24.5 166.3 64.9l-67.5 64.9C258.5 52.6 94.3 116.6 94.3 256c0 86.5 69.1 156.6 153.7 156.6 98.2 0 135-70.4 140.8-106.9H248v-85.3h236.1c2.3 12.7 3.9 24.9 3.9 41.4z"
              ></path>
            </svg>
            Google
          </Button>

          <div className="mt-4 text-center text-sm">
            {t("auth.login.noAccount")}{" "}
            <Link to="/auth/signup" className="text-primary hover:underline">
              {t("auth.login.createAccount")}
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

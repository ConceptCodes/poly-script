import { useState } from "react";
import { useForm } from "@tanstack/react-form";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { Button } from "@poly/ui";
import { Input } from "@poly/ui";
import { Label } from "@poly/ui";
import { Alert, AlertDescription } from "@poly/ui";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui";
import { apiFetch } from "../../lib/api";
import { createForgotPasswordSchema } from "./schemas";

export function ForgotPasswordPage() {
  const { t } = useTranslation();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const forgotSchema = createForgotPasswordSchema(t);

  const form = useForm({
    defaultValues: {
      email: "",
    },
  });

  const handleSubmit = async () => {
    try {
      setError(null);
      await apiFetch("/auth/forgot-password", {
        method: "POST",
        body: { email: form.state.values.email },
      });
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || t("auth.forgotPassword.error"));
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-2xl text-center">{t("auth.forgotPassword.title")}</CardTitle>
          </CardHeader>
          <CardContent>
            <Alert className="mb-6">
              <AlertDescription>{t("auth.forgotPassword.success")}</AlertDescription>
            </Alert>
            <p className="text-sm text-center text-gray-600 mb-6">
              {t("auth.forgotPassword.subtitle")}
            </p>
            <div className="flex justify-center">
              <Link to="/auth/login">
                <Button variant="outline">{t("auth.forgotPassword.backToLogin")}</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-center">{t("auth.forgotPassword.title")}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-center text-gray-600 mb-6">
            {t("auth.forgotPassword.subtitle")}
          </p>

          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit();
            }}
            className="space-y-6"
          >
            <form.Field
              name="email"
              validators={{
                onChange: ({ value }) =>
                  forgotSchema.shape.email.safeParse(value).success
                    ? undefined
                    : forgotSchema.shape.email.safeParse(value).error?.issues[0]?.message,
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor="email">{t("auth.forgotPassword.emailLabel")}</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder={t("auth.forgotPassword.emailPlaceholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    autoComplete="email"
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-sm text-destructive">
                      {field.state.meta.errors[0]}
                    </p>
                  )}
                </div>
              )}
            </form.Field>

            <Button type="submit" className="w-full" disabled={form.state.isSubmitting}>
              {form.state.isSubmitting ? t("auth.forgotPassword.sending") : t("auth.forgotPassword.sendLink")}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm">
            <Link to="/auth/login" className="text-primary hover:underline">
              {t("auth.forgotPassword.backToLogin")}
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

import { useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { useForm } from "@tanstack/react-form";
import { useTranslation } from "react-i18next";
import { Button } from "@poly/ui";
import { Input } from "@poly/ui";
import { Label } from "@poly/ui";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@poly/ui";
import { Alert, AlertDescription } from "@poly/ui";
import { Separator } from "@poly/ui";
import { apiFetch } from "../../lib/api";
import { createResetPasswordSchema } from "./schemas";

export function ResetPasswordPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const token = searchParams.get("token");
  const resetSchema = createResetPasswordSchema(t);

  const form = useForm({
    defaultValues: {
      password: "",
      confirmPassword: "",
    },
  });

  const handleSubmit = async () => {
    try {
      setError(null);
      await apiFetch("/auth/reset-password", {
        method: "POST",
        body: {
          token,
          new_password: form.state.values.password,
        },
      });
      setSuccess(true);
      setTimeout(() => navigate("/auth/login"), 3000);
    } catch (err: any) {
      setError(err.message || t("auth.resetPassword.error"));
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <Alert variant="destructive" className="max-w-md">
          <AlertDescription>{t("auth.resetPassword.error")}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-center">{t("auth.resetPassword.title")}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-center text-gray-600 mb-6">
            {t("auth.resetPassword.subtitle")}
          </p>

          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault();
              e.stopPropagation();
              handleSubmit();
            }}
            className="space-y-6"
          >
            <form.Field
              name="password"
              validators={{
                onChange: ({ value }) =>
                  resetSchema.shape.password.safeParse(value).success
                    ? undefined
                    : resetSchema.shape.password.safeParse(value).error?.issues[0]?.message,
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor="password">{t("auth.resetPassword.passwordLabel")}</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder={t("auth.resetPassword.passwordPlaceholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    autoComplete="new-password"
                  />
                </div>
              )}
            </form.Field>

            <form.Field
              name="confirmPassword"
              validators={{
                onChange: ({ value }) =>
                  (() => {
                    const result = resetSchema.safeParse({
                      ...form.state.values,
                      confirmPassword: value,
                    });
                    return result.success
                      ? undefined
                      : result.error.formErrors.fieldErrors.confirmPassword?.[0];
                  })(),
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">
                    {t("auth.resetPassword.confirmPasswordLabel")}
                  </Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder={t("auth.resetPassword.confirmPasswordPlaceholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    autoComplete="new-password"
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
              {form.state.isSubmitting
                ? t("auth.resetPassword.submitting")
                : t("auth.resetPassword.submit")}
            </Button>
          </form>

          <Separator className="my-6" />

          <div className="text-center text-sm">
            <Link to="/auth/login" className="text-primary hover:underline">
              {t("auth.resetPassword.backToLogin")}
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

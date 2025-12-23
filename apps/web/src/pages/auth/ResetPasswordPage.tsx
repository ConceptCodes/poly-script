import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useForm } from "@tanstack/react-form";
import { zodValidator } from "@tanstack/zod-form-adapter";
import { z } from "zod";
import { useTranslation } from "react-i18next";
import { Button } from "@poly/ui/components/ui/button";
import { Input } from "@poly/ui/components/ui/input";
import { Label } from "@poly/ui/components/ui/label";
import { Alert, AlertDescription } from "@poly/ui/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/components/ui/card";
import { api } from "@/lib/api";

const resetPasswordSchema = z
  .object({
    password: z.string().min(8),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "auth.passwords_do_not_match",
    path: ["confirmPassword"],
  });

export default function ResetPasswordPage() {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const token = searchParams.get("token");

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <Alert variant="destructive" className="max-w-md">
          <AlertDescription>{t("auth.invalid_reset_token")}</AlertDescription>
        </Alert>
      </div>
    );
  }

  const form = useForm({
    defaultValues: {
      password: "",
      confirmPassword: "",
    },
    onSubmit: async ({ value }) => {
      try {
        setError(null);
        await api.post("/v1/auth/reset-password", {
          token,
          new_password: value.password,
        });
        setSuccess(true);
        setTimeout(() => navigate("/auth/login"), 3000);
      } catch (err: any) {
        setError(err.response?.data?.error?.message || t("error.something_went_wrong"));
      }
    },
    validatorAdapter: zodValidator(),
  });

  const getPasswordStrength = (password: string) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;
    return strength;
  };

  const strengthLevels = ["weak", "fair", "good", "strong"];
  const strengthColors = ["bg-red-500", "bg-orange-500", "bg-yellow-500", "bg-green-500"];

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <Alert className="mb-6">
              <AlertDescription>{t("auth.password_reset_success")}</AlertDescription>
            </Alert>
            <p className="text-sm text-center text-gray-600">{t("auth.redirecting_to_login")}...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-center">{t("auth.reset_password")}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-center text-gray-600 mb-6">{t("auth.create_new_password")}</p>

          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault();
              e.stopPropagation();
              form.handleSubmit();
            }}
            className="space-y-6"
          >
            <form.Field name="password">
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor="password">{t("auth.new_password")}</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder={t("auth.new_password_placeholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    autoComplete="new-password"
                  />
                  {field.state.value && (
                    <div className="space-y-2">
                      <div className="flex gap-1 h-1">
                        {[0, 1, 2, 3].map((i) => (
                          <div
                            key={i}
                            className={`flex-1 rounded ${
                              i < getPasswordStrength(field.state.value)
                                ? strengthColors[getPasswordStrength(field.state.value) - 1]
                                : "bg-gray-200"
                            }`}
                          />
                        ))}
                      </div>
                      <p className="text-xs text-gray-600">
                        {t(
                          `auth.password_strength_${strengthLevels[Math.min(getPasswordStrength(field.state.value) - 1, 3)]}`,
                        )}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </form.Field>

            <form.Field name="confirmPassword">
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">{t("auth.confirm_password")}</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder={t("auth.confirm_password_placeholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    autoComplete="new-password"
                  />
                  {field.state.meta.touchedErrors && (
                    <p className="text-sm text-destructive">
                      {t(field.state.meta.touchedErrors[0])}
                    </p>
                  )}
                </div>
              )}
            </form.Field>

            <Button type="submit" className="w-full" disabled={form.state.isSubmitting}>
              {form.state.isSubmitting ? t("common.resetting") : t("auth.reset_password_button")}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

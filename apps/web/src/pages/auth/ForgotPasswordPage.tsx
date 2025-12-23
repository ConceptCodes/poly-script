import { useForm } from "@tanstack/react-form";
import { zodValidator } from "@tanstack/zod-form-adapter";
import { z } from "zod";
import { useTranslation } from "react-i18next";
import { Button } from "@poly/ui/components/ui/button";
import { Input } from "@poly/ui/components/ui/input";
import { Label } from "@poly/ui/components/ui/label";
import { Alert, AlertDescription } from "@poly/ui/components/ui/alert";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "@/lib/api";

const forgotPasswordSchema = z.object({
  email: z.string().min(1).email("error.invalid_email"),
});

export default function ForgotPasswordPage() {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const form = useForm({
    defaultValues: {
      email: "",
    },
    onSubmit: async ({ value }) => {
      try {
        setError(null);
        await api.post("/v1/auth/forgot-password", { email: value.email });
        setSuccess(true);
      } catch (err: any) {
        setError(err.response?.data?.error?.message || t("error.something_went_wrong"));
      }
    },
    validatorAdapter: zodValidator(),
  });

  const redirectUrl = searchParams.get("redirect") || "/dashboard";

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-2xl text-center">{t("auth.check_email")}</CardTitle>
          </CardHeader>
          <CardContent>
            <Alert className="mb-6">
              <AlertDescription>{t("auth.password_reset_email_sent")}</AlertDescription>
            </Alert>
            <p className="text-sm text-center text-gray-600 mb-6">
              {t("auth.check_email_instructions")}
            </p>
            <div className="flex justify-center">
              <Link to="/auth/login">
                <Button variant="outline">{t("common.back_to_login")}</Button>
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
          <CardTitle className="text-2xl text-center">{t("auth.forgot_password")}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-center text-gray-600 mb-6">
            {t("auth.forgot_password_instructions")}
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
              form.handleSubmit();
            }}
            className="space-y-6"
          >
            <form.Field
              name="email"
              validators={{
                onChange: forgotPasswordSchema.shape.email,
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor="email">{t("auth.email")}</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder={t("auth.email_placeholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    autoComplete="email"
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
              {form.state.isSubmitting ? t("common.sending") : t("auth.send_reset_link")}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm">
            <Link
              to={`/auth/login${redirectUrl !== "/dashboard" ? `?redirect=${redirectUrl}` : ""}`}
              className="text-primary hover:underline"
            >
              {t("common.back_to_login")}
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

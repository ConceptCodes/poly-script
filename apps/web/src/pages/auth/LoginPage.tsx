import { useForm } from "@tanstack/react-form";
import { useNavigate, Link } from "react-router-dom";
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
import { useAppStore } from "../../lib/store";
import { createLoginSchema } from "./schemas";

export function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { setUser, setAuthenticated } = useAppStore();
  const loginSchema = createLoginSchema(t);

   const form = useForm({
     defaultValues: {
       email: "",
       password: "",
     },
   });

  const handleGoogleLogin = () => {
    window.location.href = `${import.meta.env.VITE_API_URL}/auth/oauth/google`;
  };

  const handleSubmit = async () => {
    try {
      const data = (await apiFetch("/auth/login", {
        method: "POST",
        body: form.state.values,
      })) as { access_token: string; refresh_token: string };
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      const me = await apiFetch("/auth/me");
      setUser(me as any);
      setAuthenticated(true);
      navigate("/dashboard");
    } catch (error: unknown) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">{t("auth.login.title")}</CardTitle>
          <CardDescription>{t("auth.login.subtitle")}</CardDescription>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit();
            }}
            className="space-y-4"
          >
             <form.Field
               name="email"
               validators={{
                 onChange: ({ value }) =>
                   loginSchema.shape.email.safeParse(value).success
                     ? undefined
                     : loginSchema.shape.email.safeParse(value).error?.issues[0]?.message,
               }}
             >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor="email">{t("auth.login.emailLabel")}</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder={t("auth.login.emailPlaceholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                  />
                  {field.state.meta.errors && (
                    <Alert variant="destructive">
                      <AlertDescription>{field.state.meta.errors[0]}</AlertDescription>
                    </Alert>
                  )}
                </div>
              )}
            </form.Field>

             <form.Field
               name="password"
               validators={{
                 onChange: ({ value }) =>
                   loginSchema.shape.password.safeParse(value).success
                     ? undefined
                     : loginSchema.shape.password.safeParse(value).error?.issues[0]?.message,
               }}
             >
              {(field) => (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                  <Label htmlFor="password">{t("auth.login.passwordLabel")}</Label>
                  <Link
                      to="/auth/forgot-password"
                      className="text-sm text-blue-600 hover:text-blue-500"
                    >
                      {t("auth.login.forgotPassword")}
                    </Link>
                  </div>
                  <Input
                    id="password"
                    type="password"
                    placeholder={t("auth.login.passwordPlaceholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                  />
                  {field.state.meta.errors && (
                    <Alert variant="destructive">
                      <AlertDescription>{field.state.meta.errors[0]}</AlertDescription>
                    </Alert>
                  )}
                </div>
              )}
            </form.Field>

            <form.Subscribe selector={(state) => [state.canSubmit, state.isSubmitting]}>
              {([canSubmit, isSubmitting]) => (
                <Button type="submit" className="w-full" disabled={!canSubmit || isSubmitting}>
                  {isSubmitting ? t("common.loading") : t("common.submit")}
                </Button>
              )}
            </form.Subscribe>

            <form.Subscribe selector={(state) => state.errors}>
              {(errors) =>
                errors.length > 0 && (
                  <Alert variant="destructive">
                    <AlertDescription>{errors[0]}</AlertDescription>
                  </Alert>
                )
              }
            </form.Subscribe>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <Separator />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                {t("common.or")}
              </span>
            </div>
          </div>

          <Button type="button" variant="outline" className="w-full" onClick={handleGoogleLogin}>
            <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            {t("auth.login.googleButton")}
          </Button>
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          <p className="text-sm text-muted-foreground text-center">
            {t("auth.login.noAccount")}{" "}
            <Link to="/auth/signup" className="text-blue-600 hover:text-blue-500">
              {t("auth.login.signUp")}
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}

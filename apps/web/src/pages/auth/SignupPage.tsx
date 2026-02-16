import {
  Alert,
  AlertDescription,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  Checkbox,
  Input,
  Label,
  Separator,
} from "@poly/ui";
import { useForm } from "@tanstack/react-form";
import { useTranslation } from "react-i18next";
import { Link, useNavigate } from "react-router-dom";
import { apiFetch } from "../../lib/api";
import { createSignupSchema } from "./schemas";

export function SignupPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const signupSchema = createSignupSchema(t);

  const form = useForm({
    defaultValues: {
      email: "",
      password: "",
      confirmPassword: "",
      terms: false,
    },
    onSubmit: async ({ value }) => {
      try {
        await apiFetch("/auth/signup", {
          method: "POST",
          body: {
            email: value.email,
            password: value.password,
            full_name: value.email.split("@")[0],
          },
        });
        localStorage.setItem("pending_email", value.email);
        navigate("/auth/verify-email-code");
      } catch (error: unknown) {
        console.error("Signup failed:", error);
        throw error;
      }
    },
  });

  const handleGoogleSignup = () => {
    window.location.href = `${import.meta.env.VITE_API_URL}/auth/oauth/google`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">{t("auth.signup.title")}</CardTitle>
          <CardDescription>{t("auth.signup.subtitle")}</CardDescription>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              form.handleSubmit();
            }}
            className="space-y-4"
          >
            <form.Field
              name="email"
              validators={{
                onChange: ({ value }) =>
                  signupSchema.shape.email.safeParse(value).success
                    ? undefined
                    : signupSchema.shape.email.safeParse(value).error?.issues[0]?.message,
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor="email">{t("auth.signup.emailLabel")}</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder={t("auth.signup.emailPlaceholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    autoComplete="username"
                    spellCheck={false}
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
                  signupSchema.shape.password.safeParse(value).success
                    ? undefined
                    : signupSchema.shape.password.safeParse(value).error?.issues[0]?.message,
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor="password">{t("auth.signup.passwordLabel")}</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder={t("auth.signup.passwordPlaceholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    autoComplete="new-password"
                    spellCheck={false}
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
              name="confirmPassword"
              validators={{
                onChange: ({ value }) =>
                  (() => {
                    const result = signupSchema.safeParse({
                      ...form.state.values,
                      confirmPassword: value,
                    });
                    if (result.success) return undefined;
                    return result.error.issues.find((issue) =>
                      issue.path?.includes("confirmPassword"),
                    )?.message;
                  })(),
              }}
            >
              {(field) => (
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">{t("auth.signup.confirmPasswordLabel")}</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder={t("auth.signup.confirmPasswordPlaceholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    onBlur={field.handleBlur}
                    autoComplete="new-password"
                    spellCheck={false}
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
              name="terms"
              validators={{
                onChange: ({ value }) =>
                  signupSchema.shape.terms.safeParse(value).success
                    ? undefined
                    : signupSchema.shape.terms.safeParse(value).error?.issues[0]?.message,
              }}
            >
              {(field) => (
                <div className="flex items-start space-x-2">
                  <Checkbox
                    id="terms"
                    checked={field.state.value}
                    onCheckedChange={(checked) => field.handleChange(checked === true)}
                  />
                  <div className="grid gap-1.5 leading-none">
                    <Label
                      htmlFor="terms"
                      className="text-sm font-normal leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      {t("auth.signup.agreeToTerms")}
                    </Label>
                  </div>
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
              <span className="bg-background px-2 text-muted-foreground">{t("common.or")}</span>
            </div>
          </div>

          <Button type="button" variant="outline" className="w-full" onClick={handleGoogleSignup}>
            <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
              <title>Google</title>
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
            {t("auth.signup.googleButton")}
          </Button>
        </CardContent>
        <CardFooter className="flex flex-col space-y-4">
          <p className="text-sm text-muted-foreground text-center">
            {t("auth.signup.hasAccount")}{" "}
            <Link to="/auth/login" className="text-primary hover:opacity-80">
              {t("auth.signup.signIn")}
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}

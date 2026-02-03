import { Alert, AlertDescription } from "@poly/ui/alert";
import { Button } from "@poly/ui/button";
import { Input } from "@poly/ui/input";
import { Label } from "@poly/ui/label";
import { useForm } from "@tanstack/react-form";
import { AlertCircle } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import { apiFetch } from "../lib/api";
import { useAuthStore } from "../store/auth";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

export function LoginPage() {
  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [error, setError] = useState<string | null>(null);

  const form = useForm({
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const handleSubmit = async () => {
    setError(null);
    try {
      const data = await apiFetch<{
        access_token: string;
        admin_email: string;
      }>("/admin/auth/login", {
        method: "POST",
        body: form.state.values,
      });
      setAuth(data.access_token, data.admin_email);
      navigate("/");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  };

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="card-title">Admin Login</div>
        <p className="muted" style={{ marginTop: 6, marginBottom: 20 }}>
          Sign in with your super admin credentials.
        </p>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            handleSubmit();
          }}
          style={{ display: "grid", gap: 12 }}
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
              <div style={{ display: "grid", gap: 6 }}>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={field.state.value}
                  onChange={(event) => field.handleChange(event.target.value)}
                  autoComplete="email"
                  spellCheck={false}
                />
                {field.state.meta.errors?.[0] && (
                  <span className="muted" style={{ fontSize: 12 }}>
                    {field.state.meta.errors[0]}
                  </span>
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
              <div style={{ display: "grid", gap: 6 }}>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={field.state.value}
                  onChange={(event) => field.handleChange(event.target.value)}
                  autoComplete="current-password"
                  spellCheck={false}
                />
                {field.state.meta.errors?.[0] && (
                  <span className="muted" style={{ fontSize: 12 }}>
                    {field.state.meta.errors[0]}
                  </span>
                )}
              </div>
            )}
          </form.Field>
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          <Button type="submit" className="w-full">
            Sign In
          </Button>
        </form>
      </div>
    </div>
  );
}

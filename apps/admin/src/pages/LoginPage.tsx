import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "@tanstack/react-form";
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
              <label style={{ display: "grid", gap: 6 }}>
                Email
                <input
                  className="input"
                  type="email"
                  value={field.state.value}
                  onChange={(event) => field.handleChange(event.target.value)}
                />
                {field.state.meta.errors?.[0] && (
                  <span className="muted" style={{ fontSize: 12 }}>
                    {field.state.meta.errors[0]}
                  </span>
                )}
              </label>
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
              <label style={{ display: "grid", gap: 6 }}>
                Password
                <input
                  className="input"
                  type="password"
                  value={field.state.value}
                  onChange={(event) => field.handleChange(event.target.value)}
                />
                {field.state.meta.errors?.[0] && (
                  <span className="muted" style={{ fontSize: 12 }}>
                    {field.state.meta.errors[0]}
                  </span>
                )}
              </label>
            )}
          </form.Field>
          {error && (
            <div className="card" style={{ background: "#2b1720", borderColor: "#5b1b2f" }}>
              {error}
            </div>
          )}
          <button className="btn btn-primary" type="submit">
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}

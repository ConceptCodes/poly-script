const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/v1";

type ApiOptions = Omit<RequestInit, "body"> & {
  body?: Record<string, unknown> | null;
};

export async function apiFetch<T = unknown>(
  endpoint: string,
  options: ApiOptions = {},
): Promise<T> {
  const token = localStorage.getItem("admin_access_token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token && !headers.Authorization) {
    headers.Authorization = `Bearer ${token}`;
  }

  const body =
    options.body && typeof options.body === "object"
      ? JSON.stringify(options.body)
      : undefined;

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
    body: body as BodyInit,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: "An unknown error occurred",
    }));
    throw new Error(error.detail || response.statusText);
  }

  const data = await response.json().catch(() => ({}));
  return data as T;
}

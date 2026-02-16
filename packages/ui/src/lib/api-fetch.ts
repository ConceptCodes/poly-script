const API_URL =
  typeof window === "undefined"
    ? "http://localhost:8000/v1"
    : import.meta.env?.VITE_API_URL || "http://localhost:8000/v1";

export interface ApiFetchOptions {
  body?: Record<string, unknown> | FormData | null;
  headers?: Record<string, string>;
  [key: string]: unknown;
}

export interface ApiFetchConfig {
  tokenKey: "access_token" | "admin_access_token" | string;
  errorTransformer?: (error: unknown, status: number) => unknown;
  supportsFormData?: boolean;
}

const DEFAULT_ERROR_TRANSFORMER = (error: unknown, status: number) => {
  const errorRecord = (error as Record<string, unknown>) || {};
  const nestedError = errorRecord.error as Record<string, unknown> | undefined;

  if (nestedError) {
    return {
      status,
      code: nestedError.code || null,
      message: nestedError.message || "An error occurred",
      details: nestedError.details || null,
      request_id: nestedError.request_id || null,
      documentation_url: nestedError.documentation_url || null,
    };
  }

  return {
    status,
    code: errorRecord.code || null,
    message: errorRecord.message || errorRecord.detail || "An error occurred",
    details: errorRecord.details || null,
    request_id: errorRecord.request_id || null,
    documentation_url: errorRecord.documentation_url || null,
  };
};

export function createApiFetch(config: ApiFetchConfig) {
  const {
    tokenKey,
    errorTransformer = DEFAULT_ERROR_TRANSFORMER,
    supportsFormData = false,
  } = config;

  return async function apiFetch<T = unknown>(
    endpoint: string,
    options: Omit<ApiFetchOptions, "tokenKey" | "errorTransformer" | "supportsFormData"> = {},
  ): Promise<T> {
    const token = localStorage.getItem(tokenKey);
    const headers: Record<string, string> = {
      ...((options.headers as Record<string, string>) || {}),
    };

    if (supportsFormData && options.body instanceof FormData) {
      // Don't set Content-Type for FormData
    } else if (options.body && typeof options.body === "object") {
      headers["Content-Type"] = "application/json";
    }

    if (token && !headers.Authorization) {
      headers.Authorization = "Bearer " + token;
    }

    let body: BodyInit | undefined;
    if (options.body instanceof FormData) {
      body = options.body;
    } else if (options.body && typeof options.body === "object") {
      body = JSON.stringify(options.body);
    }

    const response = await fetch(API_URL + endpoint, {
      ...options,
      headers,
      body,
    });

    if (!response.ok) {
      let error: unknown;
      try {
        error = await response.json();
      } catch (_e) {
        error = { detail: "An unknown error occurred" };
      }
      const transformedError = errorTransformer(error, response.status);
      throw transformedError;
    }

    const data = await response.json().catch(() => ({}));
    return data as T;
  };
}

export { API_URL };

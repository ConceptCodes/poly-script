import { createApiFetch } from "@poly/ui";

// Create admin-specific apiFetch with:
// - admin_access_token
// - Error thrown as Error object (not error object)
export const apiFetch = createApiFetch({
  tokenKey: "admin_access_token",
  errorTransformer: (error: unknown, status: number) => {
    const errorMsg = (error as { detail?: string })?.detail || "An unknown error occurred";
    throw new Error(errorMsg);
  },
});

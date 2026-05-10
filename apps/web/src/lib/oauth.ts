import { apiFetch } from "./api";

const PKCE_VERIFIER_KEY = "oauth_pkce_verifier";
const PKCE_STATE_KEY = "oauth_pkce_state";
const PKCE_REDIRECT_KEY = "oauth_pkce_redirect";

function base64UrlEncode(bytes: Uint8Array): string {
  let binary = "";
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }

  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function createRandomString(length: number): string {
  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";
  const values = crypto.getRandomValues(new Uint8Array(length));
  return Array.from(values, (value) => alphabet[value % alphabet.length]).join("");
}

async function createCodeChallenge(verifier: string): Promise<string> {
  const data = new TextEncoder().encode(verifier);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return base64UrlEncode(new Uint8Array(digest));
}

export async function startGoogleOAuthFlow(redirectPath = "/auth/oauth/callback"): Promise<void> {
  const redirectUrl = `${window.location.origin}${redirectPath}`;
  const verifier = createRandomString(96);
  const challenge = await createCodeChallenge(verifier);
  const state = createRandomString(24);

  sessionStorage.setItem(PKCE_VERIFIER_KEY, verifier);
  sessionStorage.setItem(PKCE_STATE_KEY, state);
  sessionStorage.setItem(PKCE_REDIRECT_KEY, redirectUrl);

  const query = new URLSearchParams({
    redirect_url: redirectUrl,
    state,
    code_challenge: challenge,
    code_challenge_method: "S256",
  });
  const { auth_url } = await apiFetch<{ auth_url: string }>(
    `/auth/oauth/google?${query.toString()}`,
  );

  window.location.href = auth_url;
}

export async function finishGoogleOAuthFlow(searchParams: URLSearchParams) {
  const error = searchParams.get("error");
  if (error) {
    throw new Error(error);
  }

  const code = searchParams.get("code");
  const state = searchParams.get("state");
  const storedState = sessionStorage.getItem(PKCE_STATE_KEY);
  const codeVerifier = sessionStorage.getItem(PKCE_VERIFIER_KEY);
  const redirectUrl = sessionStorage.getItem(PKCE_REDIRECT_KEY);

  if (!code) {
    throw new Error("Missing authorization code");
  }

  if (!codeVerifier) {
    throw new Error("Missing PKCE verifier");
  }

  if (storedState && state && storedState !== state) {
    throw new Error("OAuth state mismatch");
  }

  const query = new URLSearchParams({
    code,
    state: state ?? "",
    code_verifier: codeVerifier,
  });
  if (redirectUrl) {
    query.set("redirect_url", redirectUrl);
  }

  const tokens = await apiFetch<{ access_token: string; refresh_token: string }>(
    `/auth/oauth/google/callback?${query.toString()}`,
  );

  sessionStorage.removeItem(PKCE_VERIFIER_KEY);
  sessionStorage.removeItem(PKCE_STATE_KEY);
  sessionStorage.removeItem(PKCE_REDIRECT_KEY);

  return tokens;
}

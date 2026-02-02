import { create } from "zustand";

type AuthState = {
  token: string | null;
  adminEmail: string | null;
  setAuth: (token: string, adminEmail: string) => void;
  clear: () => void;
  hydrate: () => void;
};

const STORAGE_KEY = "admin_access_token";
const EMAIL_KEY = "admin_email";

const initialToken =
  typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
const initialEmail =
  typeof window !== "undefined" ? localStorage.getItem(EMAIL_KEY) : null;

export const useAuthStore = create<AuthState>((set) => ({
  token: initialToken,
  adminEmail: initialEmail,
  setAuth: (token, adminEmail) => {
    localStorage.setItem(STORAGE_KEY, token);
    localStorage.setItem(EMAIL_KEY, adminEmail);
    set({ token, adminEmail });
  },
  clear: () => {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(EMAIL_KEY);
    set({ token: null, adminEmail: null });
  },
  hydrate: () => {
    const token = localStorage.getItem(STORAGE_KEY);
    const adminEmail = localStorage.getItem(EMAIL_KEY);
    set({ token, adminEmail });
  },
}));

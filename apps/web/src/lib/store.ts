import { create } from "zustand";
import { useTranslation } from "react-i18next";

export interface User {
  id: string;
  email: string;
  name: string;
  verified: boolean;
  createdAt: string;
  lastLogin?: string;
}

export interface Team {
  id: string;
  name: string;
  defaultLanguage: string;
  createdAt: string;
}

export interface TeamMember {
  id: string;
  userId: string;
  email: string;
  name: string;
  role: "ADMIN" | "MEMBER" | "VIEWER";
  joinedAt: string;
}

export interface TeamInvitation {
  id: string;
  teamId: string;
  email: string;
  role: "ADMIN" | "MEMBER";
  sentAt: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  team: Team | null;
  members: TeamMember[];
  invitations: TeamInvitation[];
  isLoading: boolean;
  error: string | null;
}

export interface OnboardingState {
  step: number;
  language: string;
  teamName: string;
  inviteMembers: Array<{ email: string; role: "ADMIN" | "MEMBER" }>;
}

interface AppState {
  auth: AuthState;
  onboarding: OnboardingState;
  language: string;
}

export const useAppStore = create<AppState>((set) => ({
  auth: {
    isAuthenticated: false,
    user: null,
    team: null,
    members: [],
    invitations: [],
    isLoading: false,
    error: null,
  },
  onboarding: {
    step: 1,
    language: "en",
    teamName: "",
    inviteMembers: [],
  },
  language: "en",
  setUser: (user: User) =>
    set((state) => ({
      auth: { ...state.auth, user },
    })),
  setTeam: (team: Team) =>
    set((state) => ({
      auth: { ...state.auth, team },
    })),
  setMembers: (members: TeamMember[]) =>
    set((state) => ({
      auth: { ...state.auth, members },
    })),
  setInvitations: (invitations: TeamInvitation[]) =>
    set((state) => ({
      auth: { ...state.auth, invitations },
    })),
  setAuthenticated: (isAuthenticated: boolean) =>
    set((state) => ({
      auth: { ...state.auth, isAuthenticated },
    })),
  setLoading: (isLoading: boolean) =>
    set((state) => ({
      auth: { ...state.auth, isLoading },
    })),
  setError: (error: string | null) =>
    set((state) => ({
      auth: { ...state.auth, error },
    })),
  logout: () =>
    set({
      auth: {
        isAuthenticated: false,
        user: null,
        team: null,
        members: [],
        invitations: [],
        isLoading: false,
        error: null,
      },
      onboarding: {
        step: 1,
        language: "en",
        teamName: "",
        inviteMembers: [],
      },
    }),
  setOnboardingStep: (step: number) =>
    set((state) => ({
      onboarding: { ...state.onboarding, step },
    })),
  setOnboardingLanguage: (language: string) =>
    set((state) => ({
      onboarding: { ...state.onboarding, language },
    })),
  setOnboardingTeamName: (teamName: string) =>
    set((state) => ({
      onboarding: { ...state.onboarding, teamName },
    })),
  setOnboardingInviteMembers: (inviteMembers: Array<{ email: string; role: "ADMIN" | "MEMBER" }>) =>
    set((state) => ({
      onboarding: { ...state.onboarding, inviteMembers },
    })),
  resetOnboarding: () =>
    set({
      onboarding: {
        step: 1,
        language: "en",
        teamName: "",
        inviteMembers: [],
      },
    }),
  setLanguage: (language: string) => set({ language }),
  initializeFromAuth: (user: User, team: Team) =>
    set({
      auth: {
        isAuthenticated: true,
        user,
        team,
        members: [],
        invitations: [],
        isLoading: false,
        error: null,
      },
      language: team?.defaultLanguage || "en",
    }),
}));

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
  isAuthenticated: boolean;
  user: User | null;
  team: Team | null;
  members: TeamMember[];
  invitations: TeamInvitation[];
  setAuth: (authData: Partial<AuthState>) => void;
  setUser: (user: User) => void;
  setTeam: (team: Team) => void;
  setMembers: (members: TeamMember[]) => void;
  setInvitations: (invitations: TeamInvitation[]) => void;
  setAuthenticated: (isAuthenticated: boolean) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
  setOnboardingComplete: (isComplete: boolean) => void;
  setOnboardingStep: (step: number) => void;
  setOnboardingLanguage: (language: string) => void;
  setOnboardingTeamName: (teamName: string) => void;
  setOnboardingInviteMembers: (inviteMembers: Array<{ email: string; role: "ADMIN" | "MEMBER" }>) => void;
  resetOnboarding: () => void;
  setLanguage: (language: string) => void;
  initializeFromAuth: (user: User, team: Team) => void;
}

export const useAppStore = create<AppState>((set, get) => {
  return {
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
    isAuthenticated: false,
    user: null,
    team: null,
    members: [],
    invitations: [],
    setAuth: (authData: Partial<AuthState>) =>
      set((state) => ({
        auth: { ...state.auth, ...authData },
        isAuthenticated: !!authData.isAuthenticated || state.auth.isAuthenticated,
        user: authData.user ?? state.user,
        team: authData.team ?? state.team,
        members: authData.members ?? state.members,
        invitations: authData.invitations ?? state.invitations,
      })),
    setUser: (user: User) =>
      set((state) => ({
        auth: { ...state.auth, user },
        user,
      })),
    setTeam: (team: Team) =>
      set((state) => ({
        auth: { ...state.auth, team },
        team,
      })),
    setMembers: (members: TeamMember[]) =>
      set((state) => ({
        auth: { ...state.auth, members },
        members,
      })),
    setInvitations: (invitations: TeamInvitation[]) =>
      set((state) => ({
        auth: { ...state.auth, invitations },
        invitations,
      })),
    setAuthenticated: (isAuthenticated: boolean) =>
      set((state) => ({
        auth: { ...state.auth, isAuthenticated },
        isAuthenticated,
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
        isAuthenticated: false,
        user: null,
        team: null,
        members: [],
        invitations: [],
        onboarding: {
          step: 1,
          language: "en",
          teamName: "",
          inviteMembers: [],
        },
      }),
    setOnboardingComplete: (isComplete: boolean) =>
      set((state) => ({
        auth: { ...state.auth, isLoading: isComplete },
      })),
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
      set((state) => ({
        onboarding: {
          step: 1,
          language: "en",
          teamName: "",
          inviteMembers: [],
        },
      })),
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
        isAuthenticated: true,
        user,
        team,
        members: [],
        invitations: [],
        language: team?.defaultLanguage || "en",
      }),
  };
});

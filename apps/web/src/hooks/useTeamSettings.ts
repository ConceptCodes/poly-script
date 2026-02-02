import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../lib/api";

interface TeamSettings {
  id: string;
  name: string;
  default_language: string;
  plan: string;
  credits_balance: number;
  members_count: number;
  created_at: string;
}

// Query Keys
export const teamSettingsKeys = {
  all: ["teamSettings"] as const,
  team: () => [...teamSettingsKeys.all, "team"] as const,
  members: () => [...teamSettingsKeys.all, "members"] as const,
};

// Queries
export function useTeamSettings() {
  return useQuery({
    queryKey: teamSettingsKeys.team(),
    queryFn: () => apiFetch<TeamSettings>("/v1/settings/team"),
  });
}

export function useTeamMembers() {
  return useQuery({
    queryKey: teamSettingsKeys.members(),
    queryFn: () => apiFetch<any[]>("/v1/settings/team/members"),
  });
}

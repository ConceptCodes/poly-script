import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../lib/api";

interface DashboardStats {
  total_jobs: number;
  pending_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
}

interface RecentJob {
  id: string;
  name: string;
  status: string;
  created_at: string;
  language: string;
}

interface DashboardActivity {
  type: string;
  display_name: string;
  icon: string;
  message: string;
  timestamp: string;
}

// Query Keys
export const dashboardKeys = {
  all: ["dashboard"] as const,
  stats: () => [...dashboardKeys.all, "stats"] as const,
  recentJobs: () => [...dashboardKeys.all, "recent-jobs"] as const,
  activity: () => [...dashboardKeys.all, "activity"] as const,
};

// Queries
export function useDashboardStats() {
  return useQuery({
    queryKey: dashboardKeys.stats(),
    queryFn: () => apiFetch<DashboardStats>("/dashboard/stats"),
  });
}

export function useRecentJobs() {
  return useQuery({
    queryKey: dashboardKeys.recentJobs(),
    queryFn: () => apiFetch<{ jobs: RecentJob[] }>("/dashboard/jobs/recent"),
  });
}

export function useDashboardActivity() {
  return useQuery({
    queryKey: dashboardKeys.activity(),
    queryFn: () => apiFetch<DashboardActivity[]>("/dashboard/activity"),
  });
}

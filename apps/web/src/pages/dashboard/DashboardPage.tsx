import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@poly/ui/components/ui/card";
import { Button } from "@poly/ui/components/ui/button";
import { Badge } from "@poly/ui/components/ui/badge";
import { useTranslation } from "react-i18next";
import { apiFetch } from "../../lib/api";

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

export default function DashboardPage() {
  const { t } = useTranslation();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentJobs, setRecentJobs] = useState<RecentJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [statsRes, jobsRes] = await Promise.all([
          apiFetch("/v1/dashboard/stats"),
          apiFetch("/v1/dashboard/jobs/recent"),
        ]);

        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }

        if (jobsRes.ok) {
          const jobsData = await jobsRes.json();
          setRecentJobs(jobsData.jobs || []);
        }
      } catch (error) {
        console.error("Failed to load dashboard:", error);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="h-12 w-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin mx-auto" />
          <p className="text-muted-foreground mt-4">{t("loading")}</p>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "PENDING":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "RUNNING":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      case "COMPLETED":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "FAILED":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t("dashboard.title")}</h1>
          <p className="text-muted-foreground">{t("dashboard.subtitle")}</p>
        </div>
        <Button asChild>
          <Link to="/upload">{t("dashboard.newJob")}</Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">{t("dashboard.totalJobs")}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{stats?.total_jobs || 0}</div>
            <CardDescription>{t("dashboard.allJobs")}</CardDescription>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">{t("dashboard.pendingJobs")}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-yellow-600 dark:text-yellow-400">
              {stats?.pending_jobs || 0}
            </div>
            <CardDescription>{t("dashboard.inProgress")}</CardDescription>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">{t("dashboard.completedJobs")}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-green-600 dark:text-green-400">
              {stats?.completed_jobs || 0}
            </div>
            <CardDescription>{t("dashboard.finished")}</CardDescription>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">{t("dashboard.recentJobs")}</CardTitle>
          <CardDescription>{t("dashboard.lastFiveJobs")}</CardDescription>
        </CardHeader>
        <CardContent>
          {recentJobs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>{t("dashboard.noRecentJobs")}</p>
              <Button variant="outline" className="mt-4" asChild>
                <Link to="/upload">{t("dashboard.createFirstJob")}</Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {recentJobs.map((job) => (
                <Link
                  key={job.id}
                  to={`/jobs/${job.id}`}
                  className="block p-4 border rounded-lg hover:bg-accent transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{job.name}</div>
                      <div className="text-sm text-muted-foreground mt-1">
                        {job.language} • {new Date(job.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <Badge className={getStatusColor(job.status)}>
                      {t(`status.${job.status.toLowerCase()}`)}
                    </Badge>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="bg-primary/5 border-primary/10">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">{t("dashboard.quickActions")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button asChild className="w-full">
              <Link to="/upload">{t("dashboard.uploadAudio")}</Link>
            </Button>
            <Button variant="outline" className="w-full" asChild>
              <Link to="/jobs">{t("dashboard.browseJobs")}</Link>
            </Button>
            <Button variant="outline" className="w-full" asChild>
              <Link to="/billing">{t("dashboard.manageBilling")}</Link>
            </Button>
            <Button variant="outline" className="w-full" asChild>
              <Link to="/settings/team">{t("dashboard.teamSettings")}</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold">
              {t("dashboard.accountSettings")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full" asChild>
              <Link to="/settings/user">{t("dashboard.profileSettings")}</Link>
            </Button>
            <Button variant="outline" className="w-full" asChild>
              <Link to="/settings/team">{t("dashboard.teamManagement")}</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

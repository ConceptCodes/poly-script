import { Button, Card } from "@poly/ui";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useDashboardActivity, useDashboardStats, useRecentJobs } from "../../hooks/useDashboard";

export function DashboardPage() {
  const { t } = useTranslation();

  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: jobsData, isLoading: jobsLoading } = useRecentJobs();
  const { data: activityData, isLoading: activityLoading } = useDashboardActivity();

  const loading = statsLoading || jobsLoading || activityLoading;
  const recentJobs = jobsData?.jobs || [];
  const activityItems = activityData || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="text-center">
          <div className="w-12 h-12 border-3 border-muted border-t-primary rounded-full animate-spin mx-auto mb-6" />
          <p className="text-muted-foreground text-lg">{t("loading")}</p>
        </div>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, string> = {
      PENDING: "bg-warning/10 text-warning border-warning/30",
      RUNNING: "bg-info/10 text-info border-info/30 animate-pulse",
      COMPLETED: "bg-success/10 text-success border-success/30",
      FAILED: "bg-destructive/10 text-destructive border-destructive/30",
    };
    return statusMap[status] || "bg-warning/10 text-warning border-warning/30";
  };

  return (
    <div className="bg-muted/30 min-h-screen pb-12">
      <div className="max-w-7xl mx-auto px-6 pt-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6 mb-10">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-2">
              {t("dashboard.title")}
            </h1>
            <p className="text-muted-foreground text-lg">{t("dashboard.subtitle")}</p>
          </div>
          <Button
            asChild
            className="text-base px-8 py-4 h-12 shadow-lg bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90"
          >
            <Link to="/upload">{t("dashboard.newJob")}</Link>
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <div className="relative bg-card border border-border rounded-2xl p-6 overflow-hidden transition-all hover:-translate-y-1 hover:shadow-xl before:content-[''] before:absolute before:top-0 before:left-0 before:right-0 before:h-1 before:bg-gradient-to-r before:from-primary before:to-accent">
            <div className="mb-2">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                {t("dashboard.totalJobs")}
              </h3>
            </div>
            <div className="text-5xl font-extrabold leading-none tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mb-2">
              {stats?.total_jobs || 0}
            </div>
            <p className="text-muted-foreground text-sm">{t("dashboard.allJobs")}</p>
          </div>

          <div className="relative bg-card border border-border rounded-2xl p-6 overflow-hidden transition-all hover:-translate-y-1 hover:shadow-xl before:content-[''] before:absolute before:top-0 before:left-0 before:right-0 before:h-1 before:bg-gradient-to-r before:from-warning to-warning/80">
            <div className="mb-2">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                {t("dashboard.pendingJobs")}
              </h3>
            </div>
            <div className="text-5xl font-extrabold leading-none tracking-tight bg-gradient-to-r from-warning to-warning/80 bg-clip-text text-transparent mb-2">
              {stats?.pending_jobs || 0}
            </div>
            <p className="text-muted-foreground text-sm">{t("dashboard.inProgress")}</p>
          </div>

          <div className="relative bg-card border border-border rounded-2xl p-6 overflow-hidden transition-all hover:-translate-y-1 hover:shadow-xl before:content-[''] before:absolute before:top-0 before:left-0 before:right-0 before:h-1 before:bg-gradient-to-r before:from-success to-success/80">
            <div className="mb-2">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                {t("dashboard.completedJobs")}
              </h3>
            </div>
            <div className="text-5xl font-extrabold leading-none tracking-tight bg-gradient-to-r from-success to-success/80 bg-clip-text text-transparent mb-2">
              {stats?.completed_jobs || 0}
            </div>
            <p className="text-muted-foreground text-sm">{t("dashboard.finished")}</p>
          </div>
        </div>

        <Card className="mb-10">
          <div className="p-6 pb-4">
            <h2 className="text-2xl font-bold text-foreground mb-1">{t("dashboard.recentJobs")}</h2>
            <p className="text-muted-foreground">{t("dashboard.lastFiveJobs")}</p>
          </div>
          <div className="p-6 pt-2">
            {recentJobs.length === 0 ? (
              <div className="text-center p-16 bg-muted/30 rounded-2xl border-2 border-dashed border-border">
                <div className="text-6xl mb-4 opacity-50">📋</div>
                <h3 className="text-xl font-semibold text-foreground mb-2">
                  {t("dashboard.noRecentJobs")}
                </h3>
                <p className="text-muted-foreground mb-6">{t("dashboard.startTranscribing")}</p>
                <Button
                  asChild
                  className="bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90"
                >
                  <Link to="/upload">{t("dashboard.createFirstJob")}</Link>
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {recentJobs.map((job) => (
                  <Link
                    key={job.id}
                    to={`/jobs/${job.id}`}
                    className="block relative p-5 bg-card border border-border rounded-xl transition-all hover:translate-x-1 hover:shadow-md hover:border-primary before:content-[''] before:absolute before:left-0 before:top-0 before:bottom-0 before:w-1 before:bg-gradient-to-r before:from-primary before:to-accent before:opacity-0 hover:before:opacity-100"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-foreground text-lg mb-1 truncate">
                          {job.name}
                        </h4>
                        <div className="text-muted-foreground/70 text-sm flex items-center gap-2">
                          <span className="font-medium">{job.language}</span>
                          <span className="text-muted-foreground/50">•</span>
                          <span>{new Date(job.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <span
                        className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border ${getStatusBadge(job.status)} flex-shrink-0`}
                      >
                        {t(`status.${job.status.toLowerCase()}`)}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <div className="p-6 pb-4">
              <h2 className="text-2xl font-bold text-foreground mb-1">
                {t("dashboard.quickActions")}
              </h2>
              <p className="text-muted-foreground">{t("dashboard.getStarted")}</p>
            </div>
            <div className="p-6 pt-2">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Link
                  to="/upload"
                  className="flex items-center gap-3.5 p-4 bg-card border border-border rounded-xl hover:bg-muted hover:border-primary hover:-translate-y-0.5 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-primary to-accent text-white rounded-xl flex-shrink-0 text-xl">
                    📁
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">{t("dashboard.uploadAudio")}</h4>
                    <p className="text-muted-foreground/70 text-sm mt-0.5">
                      {t("dashboard.uploadDesc")}
                    </p>
                  </div>
                </Link>

                <Link
                  to="/jobs"
                  className="flex items-center gap-3.5 p-4 bg-card border border-border rounded-xl hover:bg-muted hover:border-primary hover:-translate-y-0.5 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-primary to-accent text-white rounded-xl flex-shrink-0 text-xl">
                    🔍
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">{t("dashboard.browseJobs")}</h4>
                    <p className="text-muted-foreground/70 text-sm mt-0.5">
                      {t("dashboard.browseDesc")}
                    </p>
                  </div>
                </Link>

                <Link
                  to="/billing"
                  className="flex items-center gap-3.5 p-4 bg-card border border-border rounded-xl hover:bg-muted hover:border-primary hover:-translate-y-0.5 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-primary to-accent text-white rounded-xl flex-shrink-0 text-xl">
                    💳
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">
                      {t("dashboard.manageBilling")}
                    </h4>
                    <p className="text-muted-foreground/70 text-sm mt-0.5">
                      {t("dashboard.billingDesc")}
                    </p>
                  </div>
                </Link>

                <Link
                  to="/settings/team"
                  className="flex items-center gap-3.5 p-4 bg-card border border-border rounded-xl hover:bg-muted hover:border-primary hover:-translate-y-0.5 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-primary to-accent text-white rounded-xl flex-shrink-0 text-xl">
                    👥
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">{t("dashboard.teamSettings")}</h4>
                    <p className="text-muted-foreground/70 text-sm mt-0.5">
                      {t("dashboard.teamDesc")}
                    </p>
                  </div>
                </Link>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6 pb-4">
              <h2 className="text-2xl font-bold text-foreground mb-1">
                {t("dashboard.accountSettings")}
              </h2>
              <p className="text-muted-foreground">{t("dashboard.manageAccount")}</p>
            </div>
            <div className="p-6 pt-2">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Link
                  to="/settings/user"
                  className="flex items-center gap-3.5 p-4 bg-card border border-border rounded-xl hover:bg-muted hover:border-primary hover:-translate-y-0.5 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-primary to-accent text-white rounded-xl flex-shrink-0 text-xl">
                    👤
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">
                      {t("dashboard.profileSettings")}
                    </h4>
                    <p className="text-muted-foreground/70 text-sm mt-0.5">
                      {t("dashboard.profileDesc")}
                    </p>
                  </div>
                </Link>

                <Link
                  to="/settings/team"
                  className="flex items-center gap-3.5 p-4 bg-card border border-border rounded-xl hover:bg-muted hover:border-primary hover:-translate-y-0.5 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-primary to-accent text-white rounded-xl flex-shrink-0 text-xl">
                    ⚙️
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">
                      {t("dashboard.teamManagement")}
                    </h4>
                    <p className="text-muted-foreground/70 text-sm mt-0.5">
                      {t("dashboard.teamManageDesc")}
                    </p>
                  </div>
                </Link>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6 pb-4">
              <h2 className="text-2xl font-bold text-foreground mb-1">
                {t("dashboard.activityFeed")}
              </h2>
              <p className="text-muted-foreground">{t("dashboard.activityDesc")}</p>
            </div>
            <div className="p-6 pt-2">
              {activityItems.length === 0 ? (
                <div className="text-sm text-muted-foreground">{t("dashboard.noActivity")}</div>
              ) : (
                <div className="space-y-3">
                  {activityItems.map((item) => (
                    <div
                      key={`${item.type}-${item.timestamp}`}
                      className="flex items-start gap-3 rounded-xl border border-border bg-card p-4"
                    >
                      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-primary">
                        {item.icon}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-foreground">{item.display_name}</p>
                        <p className="text-sm text-muted-foreground">{item.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

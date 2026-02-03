import { Button } from "@poly/ui";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useDashboardStats, useRecentJobs } from "../../hooks/useDashboard";

const dashboardTheme = `
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');

  :root {
    /* Primary Colors */
    --precision-primary: #4F46E5;
    --precision-primary-hover: #4338ca;
    --precision-accent: #8B5CF6;
    --precision-accent-light: #a78bfa;

    /* Background Colors */
    --precision-bg-cream: #FAFAF9;
    --precision-bg-white: #ffffff;
    --precision-bg-subtle: #f5f5f4;

    /* Status Colors */
    --precision-success: #10B981;
    --precision-success-light: #d1fae5;
    --precision-warning: #F59E0B;
    --precision-warning-light: #fef3c7;
    --precision-error: #ef4444;
    --precision-error-light: #fee2e2;
    --precision-info: #3b82f6;
    --precision-info-light: #dbeafe;

    /* Text Colors */
    --precision-text-primary: #1c1917;
    --precision-text-secondary: #57534e;
    --precision-text-tertiary: #a8a29e;

    /* Border Colors */
    --precision-border: #e7e5e4;
    --precision-border-hover: #d6d3d1;

    /* Shadows */
    --precision-shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --precision-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
    --precision-shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --precision-shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    --precision-shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);

    /* Gradients */
    --precision-gradient-primary: linear-gradient(135deg, #4F46E5 0%, #8B5CF6 100%);
    --precision-gradient-success: linear-gradient(135deg, #10B981 0%, #059669 100%);
    --precision-gradient-warning: linear-gradient(135deg, #F59E0B 0%, #d97706 100%);
    --precision-gradient-error: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    --precision-gradient-info: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  }

  /* Noise texture overlay */
  .precision-noise-bg {
    position: relative;
    background-color: var(--precision-bg-cream);
  }

  .precision-noise-bg::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
    opacity: 0.03;
    pointer-events: none;
  }

  /* Typography */
  .precision-font-heading {
    font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  }

  .precision-font-body {
    font-family: 'DM Sans', system-ui, -apple-system, sans-serif;
  }

  /* Enhanced Card Styling */
  .precision-card {
    position: relative;
    background: var(--precision-bg-white);
    border: 1px solid var(--precision-border);
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: var(--precision-shadow-sm);
  }

  .precision-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--precision-gradient-primary);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .precision-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--precision-shadow-lg);
    border-color: var(--precision-border-hover);
  }

  .precision-card:hover::before {
    opacity: 1;
  }

  /* Stat Card Variants */
  .precision-stat-card {
    position: relative;
    background: var(--precision-bg-white);
    border: 1px solid var(--precision-border);
    border-radius: 16px;
    padding: 1.5rem;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: var(--precision-shadow);
  }

  .precision-stat-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    border-radius: 16px 16px 0 0;
    opacity: 1;
    transition: all 0.3s ease;
  }

  .precision-stat-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--precision-shadow-xl);
  }

  .precision-stat-card-primary::before {
    background: var(--precision-gradient-primary);
  }

  .precision-stat-card-warning::before {
    background: var(--precision-gradient-warning);
  }

  .precision-stat-card-success::before {
    background: var(--precision-gradient-success);
  }

  /* Status Badge Styling */
  .precision-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.375rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'Plus Jakarta Sans', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 0.2s ease;
    border: 1px solid transparent;
  }

  .precision-badge-pending {
    background: var(--precision-warning-light);
    color: #92400e;
    border-color: #fcd34d;
  }

  .precision-badge-running {
    background: var(--precision-info-light);
    color: #1e40af;
    border-color: #93c5fd;
    animation: pulse-badge 2s ease-in-out infinite;
  }

  .precision-badge-completed {
    background: var(--precision-success-light);
    color: #065f46;
    border-color: #6ee7b7;
  }

  .precision-badge-failed {
    background: var(--precision-error-light);
    color: #991b1b;
    border-color: #fca5a5;
  }

  @keyframes pulse-badge {
    0%, 100% {
      box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4);
    }
    50% {
      box-shadow: 0 0 0 8px rgba(59, 130, 246, 0);
    }
  }

  /* Job List Item Styling */
  .precision-job-item {
    display: block;
    position: relative;
    padding: 1.25rem 1.5rem;
    background: var(--precision-bg-white);
    border: 1px solid var(--precision-border);
    border-radius: 12px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    text-decoration: none;
    overflow: hidden;
  }

  .precision-job-item::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: var(--precision-gradient-primary);
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .precision-job-item:hover {
    transform: translateX(4px);
    box-shadow: var(--precision-shadow-md);
    border-color: var(--precision-primary);
  }

  .precision-job-item:hover::before {
    opacity: 1;
  }

  /* Button Styling */
  .precision-button-primary {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.5rem;
    background: var(--precision-gradient-primary);
    color: white;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
    border-radius: 10px;
    border: none;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: var(--precision-shadow-sm);
    text-decoration: none;
    font-size: 0.9375rem;
  }

  .precision-button-primary:hover {
    transform: translateY(-2px);
    box-shadow: var(--precision-shadow-lg);
  }

  .precision-button-primary:active {
    transform: translateY(0);
  }

  .precision-button-secondary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem 1.5rem;
    background: var(--precision-bg-white);
    color: var(--precision-text-primary);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
    border-radius: 10px;
    border: 1px solid var(--precision-border);
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    text-decoration: none;
    font-size: 0.9375rem;
  }

  .precision-button-secondary:hover {
    background: var(--precision-bg-subtle);
    border-color: var(--precision-border-hover);
    transform: translateY(-1px);
    box-shadow: var(--precision-shadow-sm);
  }

  /* Quick Action Grid */
  .precision-action-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1rem;
  }

  .precision-action-item {
    display: flex;
    align-items: center;
    gap: 0.875rem;
    padding: 1rem 1.25rem;
    background: var(--precision-bg-white);
    border: 1px solid var(--precision-border);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    text-decoration: none;
    color: var(--precision-text-primary);
  }

  .precision-action-item:hover {
    background: var(--precision-bg-subtle);
    border-color: var(--precision-primary);
    transform: translateY(-2px);
    box-shadow: var(--precision-shadow-md);
  }

  .precision-action-item-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background: var(--precision-gradient-primary);
    color: white;
    border-radius: 10px;
    flex-shrink: 0;
    font-size: 1.125rem;
  }

  /* Empty State */
  .precision-empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background: var(--precision-bg-subtle);
    border-radius: 16px;
    border: 2px dashed var(--precision-border);
  }

  .precision-empty-state-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }

  /* Loading Spinner */
  .precision-spinner {
    border: 3px solid var(--precision-border);
    border-top-color: var(--precision-primary);
    border-radius: 50%;
    width: 48px;
    height: 48px;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Container Width */
  .precision-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 1.5rem;
  }

  /* Stat Number Styling */
  .precision-stat-number {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 3.5rem;
    line-height: 1;
    letter-spacing: -0.02em;
    background: var(--precision-gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  /* Text Colors */
  .precision-text-primary {
    color: var(--precision-text-primary);
  }

  .precision-text-secondary {
    color: var(--precision-text-secondary);
  }

  .precision-text-tertiary {
    color: var(--precision-text-tertiary);
  }

  /* Stat Card Colors */
  .precision-stat-primary .precision-stat-number {
    background: var(--precision-gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .precision-stat-warning .precision-stat-number {
    background: var(--precision-gradient-warning);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .precision-stat-success .precision-stat-number {
    background: var(--precision-gradient-success);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
`;

export function DashboardPage() {
  const { t } = useTranslation();

  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: jobsData, isLoading: jobsLoading } = useRecentJobs();

  const loading = statsLoading || jobsLoading;
  const recentJobs = jobsData?.jobs || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="text-center">
          <div className="precision-spinner mx-auto mb-6" />
          <p className="precision-text-secondary precision-font-body text-lg">{t("loading")}</p>
        </div>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, string> = {
      PENDING: "precision-badge-pending",
      RUNNING: "precision-badge-running",
      COMPLETED: "precision-badge-completed",
      FAILED: "precision-badge-failed",
    };
    return statusMap[status] || "precision-badge-pending";
  };

  return (
    <>
      <style>{dashboardTheme}</style>
      <div className="precision-noise-bg min-h-screen pb-12">
        <div className="precision-container pt-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6 mb-10">
            <div>
              <h1 className="precision-font-heading text-4xl md:text-5xl font-bold precision-text-primary mb-2">
                {t("dashboard.title")}
              </h1>
              <p className="precision-font-body precision-text-secondary text-lg">
                {t("dashboard.subtitle")}
              </p>
            </div>
            <Button asChild className="precision-button-primary text-base px-8 py-4 h-12 shadow-lg">
              <Link to="/upload">{t("dashboard.newJob")}</Link>
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            <div className="precision-stat-card precision-stat-card-primary">
              <div className="mb-2">
                <h3 className="precision-font-heading text-sm font-semibold precision-text-tertiary uppercase tracking-wider">
                  {t("dashboard.totalJobs")}
                </h3>
              </div>
              <div className="precision-stat-number precision-stat-primary mb-2">
                {stats?.total_jobs || 0}
              </div>
              <p className="precision-font-body precision-text-secondary text-sm">
                {t("dashboard.allJobs")}
              </p>
            </div>

            <div className="precision-stat-card precision-stat-card-warning">
              <div className="mb-2">
                <h3 className="precision-font-heading text-sm font-semibold precision-text-tertiary uppercase tracking-wider">
                  {t("dashboard.pendingJobs")}
                </h3>
              </div>
              <div className="precision-stat-number precision-stat-warning mb-2">
                {stats?.pending_jobs || 0}
              </div>
              <p className="precision-font-body precision-text-secondary text-sm">
                {t("dashboard.inProgress")}
              </p>
            </div>

            <div className="precision-stat-card precision-stat-card-success">
              <div className="mb-2">
                <h3 className="precision-font-heading text-sm font-semibold precision-text-tertiary uppercase tracking-wider">
                  {t("dashboard.completedJobs")}
                </h3>
              </div>
              <div className="precision-stat-number precision-stat-success mb-2">
                {stats?.completed_jobs || 0}
              </div>
              <p className="precision-font-body precision-text-secondary text-sm">
                {t("dashboard.finished")}
              </p>
            </div>
          </div>

          <div className="precision-card mb-10">
            <div className="p-6 pb-4">
              <h2 className="precision-font-heading text-2xl font-bold precision-text-primary mb-1">
                {t("dashboard.recentJobs")}
              </h2>
              <p className="precision-font-body precision-text-secondary">
                {t("dashboard.lastFiveJobs")}
              </p>
            </div>
            <div className="p-6 pt-2">
              {recentJobs.length === 0 ? (
                <div className="precision-empty-state">
                  <div className="precision-empty-state-icon">📋</div>
                  <h3 className="precision-font-heading text-xl font-semibold precision-text-primary mb-2">
                    {t("dashboard.noRecentJobs")}
                  </h3>
                  <p className="precision-font-body precision-text-secondary mb-6">
                    {t("dashboard.startTranscribing")}
                  </p>
                  <Button asChild className="precision-button-primary">
                    <Link to="/upload">{t("dashboard.createFirstJob")}</Link>
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentJobs.map((job) => (
                    <Link key={job.id} to={`/jobs/${job.id}`} className="precision-job-item">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <h4 className="precision-font-heading font-semibold precision-text-primary text-lg mb-1 truncate">
                            {job.name}
                          </h4>
                          <div className="precision-font-body precision-text-tertiary text-sm flex items-center gap-2">
                            <span className="font-medium">{job.language}</span>
                            <span className="text-gray-300">•</span>
                            <span>{new Date(job.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                        <span
                          className={`precision-badge ${getStatusBadge(job.status)} flex-shrink-0`}
                        >
                          {t(`status.${job.status.toLowerCase()}`)}
                        </span>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="precision-card">
              <div className="p-6 pb-4">
                <h2 className="precision-font-heading text-2xl font-bold precision-text-primary mb-1">
                  {t("dashboard.quickActions")}
                </h2>
                <p className="precision-font-body precision-text-secondary">
                  {t("dashboard.getStarted")}
                </p>
              </div>
              <div className="p-6 pt-2">
                <div className="precision-action-grid">
                  <Link to="/upload" className="precision-action-item">
                    <div className="precision-action-item-icon">📁</div>
                    <div>
                      <h4 className="precision-font-heading font-semibold precision-text-primary">
                        {t("dashboard.uploadAudio")}
                      </h4>
                      <p className="precision-font-body precision-text-tertiary text-sm mt-0.5">
                        {t("dashboard.uploadDesc")}
                      </p>
                    </div>
                  </Link>

                  <Link to="/jobs" className="precision-action-item">
                    <div className="precision-action-item-icon">🔍</div>
                    <div>
                      <h4 className="precision-font-heading font-semibold precision-text-primary">
                        {t("dashboard.browseJobs")}
                      </h4>
                      <p className="precision-font-body precision-text-tertiary text-sm mt-0.5">
                        {t("dashboard.browseDesc")}
                      </p>
                    </div>
                  </Link>

                  <Link to="/billing" className="precision-action-item">
                    <div className="precision-action-item-icon">💳</div>
                    <div>
                      <h4 className="precision-font-heading font-semibold precision-text-primary">
                        {t("dashboard.manageBilling")}
                      </h4>
                      <p className="precision-font-body precision-text-tertiary text-sm mt-0.5">
                        {t("dashboard.billingDesc")}
                      </p>
                    </div>
                  </Link>

                  <Link to="/settings/team" className="precision-action-item">
                    <div className="precision-action-item-icon">👥</div>
                    <div>
                      <h4 className="precision-font-heading font-semibold precision-text-primary">
                        {t("dashboard.teamSettings")}
                      </h4>
                      <p className="precision-font-body precision-text-tertiary text-sm mt-0.5">
                        {t("dashboard.teamDesc")}
                      </p>
                    </div>
                  </Link>
                </div>
              </div>
            </div>

            <div className="precision-card">
              <div className="p-6 pb-4">
                <h2 className="precision-font-heading text-2xl font-bold precision-text-primary mb-1">
                  {t("dashboard.accountSettings")}
                </h2>
                <p className="precision-font-body precision-text-secondary">
                  {t("dashboard.manageAccount")}
                </p>
              </div>
              <div className="p-6 pt-2">
                <div className="precision-action-grid">
                  <Link to="/settings/user" className="precision-action-item">
                    <div className="precision-action-item-icon">👤</div>
                    <div>
                      <h4 className="precision-font-heading font-semibold precision-text-primary">
                        {t("dashboard.profileSettings")}
                      </h4>
                      <p className="precision-font-body precision-text-tertiary text-sm mt-0.5">
                        {t("dashboard.profileDesc")}
                      </p>
                    </div>
                  </Link>

                  <Link to="/settings/team" className="precision-action-item">
                    <div className="precision-action-item-icon">⚙️</div>
                    <div>
                      <h4 className="precision-font-heading font-semibold precision-text-primary">
                        {t("dashboard.teamManagement")}
                      </h4>
                      <p className="precision-font-body precision-text-tertiary text-sm mt-0.5">
                        {t("dashboard.teamManageDesc")}
                      </p>
                    </div>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

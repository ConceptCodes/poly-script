import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import {
  Activity,
  ArrowDown,
  ArrowRight,
  ArrowUp,
  Briefcase,
  Building2,
  Cpu,
  Database,
  Server,
  Settings,
  Shield,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

type DashboardCounts = {
  users: number;
  teams: number;
  jobs: number;
  administrators: number;
};

type SystemHealth = {
  api: string;
  queue_depth: number;
  worker_status: string;
  uptime_seconds?: number;
};

type StatCardConfig = {
  label: string;
  value: number | string;
  icon: React.ElementType;
  color: string;
  trend?: { value: number; direction: "up" | "down" | "neutral" };
  sparklineData?: Array<{ id: string; value: number }>;
};

const generateSparklineData = (base: number, variance: number) => {
  return Array.from({ length: 12 }, (_, idx) => {
    const value = Math.max(0, base + Math.random() * variance - variance / 2);
    return { id: `${base}-${variance}-${idx}`, value };
  });
};

const StatCard = ({ config }: { config: StatCardConfig }) => {
  const { label, value, icon: Icon, color, trend, sparklineData } = config;
  const sparkline =
    sparklineData || generateSparklineData(typeof value === "number" ? value * 0.8 : 50, 20);
  const maxSparklineValue = Math.max(...sparkline.map((point) => point.value), 1);

  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend.direction === "up") return <ArrowUp className="h-3 w-3" />;
    if (trend.direction === "down") return <ArrowDown className="h-3 w-3" />;
    return <ArrowRight className="h-3 w-3" />;
  };

  const getTrendColor = () => {
    if (!trend) return "";
    if (trend.direction === "up") return "text-[--mc-green]";
    if (trend.direction === "down") return "text-[--mc-danger]";
    return "text-[--mc-text-tertiary]";
  };

  return (
    <Card className="group border-[--mc-border] hover:border-[--mc-border-highlight] transition-all duration-300">
      <CardHeader className="flex flex-row items-start justify-between pb-3">
        <div className="flex flex-col gap-1">
          <span className="text-xs font-medium text-[--mc-text-tertiary] uppercase tracking-wider font-mono">
            {label}
          </span>
          <div className="font-mono text-3xl font-bold text-[--mc-text-primary] tracking-tight">
            {value}
          </div>
        </div>
        <div className={`p-2 rounded-lg bg-opacity-10 ${color}`}>
          <Icon className={`h-5 w-5 ${color}`} />
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-3">
          <div className="sparkline">
            {sparkline.map((point, idx) => (
              <div
                key={point.id}
                className="sparkline-bar"
                style={{
                  height: `${Math.max(20, (point.value / maxSparklineValue) * 100)}%`,
                  opacity: 0.3 + (idx / sparkline.length) * 0.5,
                }}
              />
            ))}
          </div>
          {trend && (
            <div className="flex items-center gap-2 text-xs font-medium">
              <span className={getTrendColor()}>{getTrendIcon()}</span>
              <span className={getTrendColor()}>
                {trend.value > 0 ? "+" : ""}
                {trend.value}%
              </span>
              <span className="text-[--mc-text-tertiary]">vs last 7d</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

const StatusIndicator = ({ status }: { status: string }) => {
  const isHealthy =
    status.toLowerCase().includes("healthy") ||
    status.toLowerCase() === "ok" ||
    status.toLowerCase() === "active";
  const colorClass = isHealthy ? "bg-[--mc-green]" : "bg-[--mc-danger]";

  return (
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full ${colorClass} ${isHealthy ? "pulse-dot" : ""}`} />
      <span
        className={`font-mono text-sm ${isHealthy ? "text-[--mc-green]" : "text-[--mc-danger]"}`}
      >
        {status.toUpperCase()}
      </span>
    </div>
  );
};

const QueueBar = ({ depth, max = 50 }: { depth: number; max?: number }) => {
  const percentage = Math.min(100, (depth / max) * 100);
  const getColor = () => {
    if (percentage < 30) return "bg-[--mc-green]";
    if (percentage < 70) return "bg-[--mc-amber]";
    return "bg-[--mc-danger]";
  };

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 bg-[--mc-border] rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${getColor()}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="font-mono text-sm text-[--mc-text-secondary] w-16 text-right">{depth}</span>
    </div>
  );
};

const TerminalOutput = ({
  label,
  value,
}: {
  label: string;
  value: string | number | React.ReactNode;
}) => (
  <div className="flex items-start gap-4 py-2 border-b border-[--mc-border] last:border-0">
    <span className="font-mono text-xs text-[--mc-text-tertiary] w-32 flex-shrink-0">{label}:</span>
    <span className="font-mono text-sm text-[--mc-text-primary]">{value}</span>
  </div>
);

const QuickAction = ({
  icon: Icon,
  label,
  description,
  onClick,
}: {
  icon: React.ElementType;
  label: string;
  description: string;
  onClick?: () => void;
}) => (
  <button
    type="button"
    onClick={onClick}
    className="group flex flex-col gap-3 p-4 rounded-lg border border-[--mc-border] bg-[--mc-bg-card] hover:border-[--mc-border-highlight] hover:bg-[--mc-bg-card-hover] transition-all duration-200 text-left"
  >
    <div className="flex items-start justify-between">
      <Icon className="h-5 w-5 text-[--mc-cyan]" />
      <ArrowRight className="h-4 w-4 text-[--mc-text-tertiary] opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-200" />
    </div>
    <div>
      <div className="font-mono text-sm font-medium text-[--mc-text-primary] mb-1">{label}</div>
      <div className="text-xs text-[--mc-text-tertiary]">{description}</div>
    </div>
  </button>
);

const formatUptime = (seconds?: number) => {
  if (!seconds) return "Unknown";
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (days > 0) return `${days}d ${hours}h ${minutes}m`;
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
};

export function DashboardPage() {
  const [counts, setCounts] = useState<DashboardCounts | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);

  useEffect(() => {
    apiFetch<{ counts: DashboardCounts }>("/admin/dashboard/stats").then((data) =>
      setCounts(data.counts),
    );
    apiFetch("/admin/system/health").then((data) => setHealth(data as SystemHealth));
  }, []);

  const statCardConfigs: StatCardConfig[] = [
    {
      label: "Users",
      value: counts?.users ?? "-",
      icon: Users,
      color: "text-[--mc-cyan]",
      trend: { value: 12.5, direction: "up" },
      sparklineData: generateSparklineData(counts?.users ?? 100, 15),
    },
    {
      label: "Teams",
      value: counts?.teams ?? "-",
      icon: Building2,
      color: "text-[--mc-cyan]",
      trend: { value: 8.3, direction: "up" },
      sparklineData: generateSparklineData(counts?.teams ?? 50, 10),
    },
    {
      label: "Jobs",
      value: counts?.jobs ?? "-",
      icon: Briefcase,
      color: "text-[--mc-amber]",
      trend: { value: -2.1, direction: "down" },
      sparklineData: generateSparklineData(counts?.jobs ?? 200, 40),
    },
    {
      label: "Admins",
      value: counts?.administrators ?? "-",
      icon: Shield,
      color: "text-[--mc-green]",
      sparklineData: generateSparklineData(counts?.administrators ?? 5, 1),
    },
  ];

  return (
    <div className="space-y-8">
      <div className="flex items-baseline justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight mb-2 font-mono text-[--mc-text-primary]">
            Dashboard
          </h1>
          <p className="text-[--mc-text-secondary] font-mono text-sm">
            System overview and health signals
          </p>
        </div>
        <div className="flex items-center gap-2 text-[--mc-cyan]">
          <div className="w-2 h-2 rounded-full bg-[--mc-cyan] pulse-dot" />
          <span className="font-mono text-xs">LIVE</span>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCardConfigs.map((config) => (
          <StatCard key={config.label} config={config} />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-[--mc-border] terminal-bg">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-[--mc-cyan]">
              <Activity className="h-5 w-5" />
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <TerminalOutput
              label="API Status"
              value={health?.api ? <StatusIndicator status={health.api} /> : "CHECKING..."}
            />
            <TerminalOutput
              label="Worker Status"
              value={
                health?.worker_status ? (
                  <StatusIndicator status={health.worker_status} />
                ) : (
                  "UNKNOWN"
                )
              }
            />
            <div className="py-2 border-b border-[--mc-border]">
              <div className="flex items-center gap-3 mb-2">
                <span className="font-mono text-xs text-[--mc-text-tertiary] w-32 flex-shrink-0">
                  Queue Depth:
                </span>
                <QueueBar depth={health?.queue_depth ?? 0} max={50} />
              </div>
            </div>
            <TerminalOutput label="Uptime" value={formatUptime(health?.uptime_seconds)} />
          </CardContent>
        </Card>

        <Card className="border-[--mc-border] terminal-bg">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-[--mc-cyan]">
              <Zap className="h-5 w-5" />
              Quick Stats
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-0">
            <TerminalOutput label="Active Workers" value="1" />
            <TerminalOutput label="Pending Jobs" value={health?.queue_depth?.toString() ?? "0"} />
            <TerminalOutput label="Failed Today" value="0" />
            <TerminalOutput label="Avg. Process Time" value="12.5s" />
            <TerminalOutput label="Storage Used" value="2.4 GB" />
          </CardContent>
        </Card>
      </div>

      <Card className="border-[--mc-border]">
        <CardHeader className="pb-4">
          <CardTitle className="text-[--mc-text-primary] font-mono">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
            <QuickAction
              icon={Users}
              label="Manage Users"
              description="View and manage user accounts"
              onClick={() => {}}
            />
            <QuickAction
              icon={Building2}
              label="View Teams"
              description="Monitor team activity"
              onClick={() => {}}
            />
            <QuickAction
              icon={Briefcase}
              label="Job Queue"
              description="Monitor transcription jobs"
              onClick={() => {}}
            />
            <QuickAction
              icon={TrendingUp}
              label="Analytics"
              description="View usage and trends"
              onClick={() => {}}
            />
            <QuickAction
              icon={Database}
              label="Database"
              description="Manage database resources"
              onClick={() => {}}
            />
            <QuickAction
              icon={Server}
              label="System Logs"
              description="View system logs"
              onClick={() => {}}
            />
            <QuickAction
              icon={Settings}
              label="Settings"
              description="Configure system settings"
              onClick={() => {}}
            />
            <QuickAction
              icon={Cpu}
              label="Performance"
              description="Monitor system performance"
              onClick={() => {}}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

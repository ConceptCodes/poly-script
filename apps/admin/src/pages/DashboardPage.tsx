import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@poly/ui/card";
import { Badge } from "@poly/ui/badge";
import { Activity, Users, Building2, Briefcase, CheckCircle, XCircle, Clock, Zap, Shield } from "lucide-react";

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

export function DashboardPage() {
  const [counts, setCounts] = useState<DashboardCounts | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);

  useEffect(() => {
    apiFetch<{ counts: DashboardCounts }>("/admin/dashboard/stats").then((data) =>
      setCounts(data.counts),
    );
    apiFetch("/admin/system/health").then((data) => setHealth(data as SystemHealth));
  }, []);

  const getHealthBadge = (status: string) => {
    const isHealthy = status.toLowerCase().includes("healthy") || status.toLowerCase() === "ok";
    return (
      <Badge variant={isHealthy ? "default" : "destructive"}>
        {status}
      </Badge>
    );
  };

  const statCards = [
    { label: "Users", value: counts?.users ?? "-", icon: Users, color: "text-blue-400" },
    { label: "Teams", value: counts?.teams ?? "-", icon: Building2, color: "text-purple-400" },
    { label: "Jobs", value: counts?.jobs ?? "-", icon: Briefcase, color: "text-amber-400" },
    { label: "Admins", value: counts?.administrators ?? "-", icon: Shield, color: "text-green-400" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Dashboard</h1>
        <p className="text-muted-foreground">System overview and health signals.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.label} className="border-border">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {item.label}
                </CardTitle>
                <Icon className={`h-5 w-5 ${item.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{item.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">API Status</span>
              {health?.api ? getHealthBadge(health.api) : <Badge variant="outline">Checking...</Badge>}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Queue Depth</span>
              <span className="font-medium">{health?.queue_depth ?? "-"}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Worker Status</span>
              {health?.worker_status ? getHealthBadge(health.worker_status) : <Badge variant="outline">Unknown</Badge>}
            </div>
            {health?.uptime_seconds && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Uptime</span>
                <span className="font-medium">{Math.floor(health.uptime_seconds / 60)}m</span>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Quick Stats
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span className="text-sm text-muted-foreground">Active Workers</span>
              </div>
              <span className="font-medium">1</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-blue-500" />
                <span className="text-sm text-muted-foreground">Pending Jobs</span>
              </div>
              <span className="font-medium">{health?.queue_depth ?? "-"}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <XCircle className="h-4 w-4 text-red-500" />
                <span className="text-sm text-muted-foreground">Failed Today</span>
              </div>
              <span className="text-muted-foreground text-sm">Coming soon</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

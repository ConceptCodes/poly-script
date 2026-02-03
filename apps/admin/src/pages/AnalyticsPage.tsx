import { Badge } from "@poly/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@poly/ui/select";
import {
  AlertCircle,
  BarChart3,
  Briefcase,
  Building2,
  Calendar,
  CheckCircle,
  Clock,
  Users,
  XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

type UsageData = {
  users: number;
  teams: number;
  jobs: number;
  successful_jobs: number;
};

type ErrorData = {
  total_errors: number;
  failed_jobs: number;
  canceled_jobs: number;
};

type TimeRange = "7d" | "30d" | "90d" | "all";

export function AnalyticsPage() {
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [errors, setErrors] = useState<ErrorData | null>(null);
  const [timeRange, setTimeRange] = useState<TimeRange>("30d");

  useEffect(() => {
    apiFetch<UsageData>("/admin/analytics/usage").then(setUsage);
    apiFetch<ErrorData>("/admin/analytics/errors").then(setErrors);
  }, []);

  const timeRanges: { value: TimeRange; label: string }[] = [
    { value: "7d", label: "7 days" },
    { value: "30d", label: "30 days" },
    { value: "90d", label: "90 days" },
    { value: "all", label: "All time" },
  ];

  const metrics = [
    { label: "Users", value: usage?.users ?? "-", icon: Users, color: "text-blue-400" },
    { label: "Teams", value: usage?.teams ?? "-", icon: Building2, color: "text-purple-400" },
    { label: "Total Jobs", value: usage?.jobs ?? "-", icon: Briefcase, color: "text-amber-400" },
    {
      label: "Successful Jobs",
      value: usage?.successful_jobs ?? "-",
      icon: CheckCircle,
      color: "text-green-400",
    },
  ];

  const errorMetrics = [
    {
      label: "Total Errors",
      value: errors?.total_errors ?? "-",
      icon: AlertCircle,
      color: "text-red-400",
    },
    {
      label: "Failed Jobs",
      value: errors?.failed_jobs ?? "-",
      icon: XCircle,
      color: "text-orange-400",
    },
    {
      label: "Canceled Jobs",
      value: errors?.canceled_jobs ?? "-",
      icon: Clock,
      color: "text-slate-400",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Analytics</h1>
          <p className="text-muted-foreground">Usage and reliability snapshots.</p>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-muted-foreground" />
          <Select value={timeRange} onValueChange={(value) => setTimeRange(value as TimeRange)}>
            <SelectTrigger className="w-[130px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {timeRanges.map((range) => (
                <SelectItem key={range.value} value={range.value}>
                  {range.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metrics.map((item) => {
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
              <BarChart3 className="h-5 w-5" />
              Error Trends
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {errorMetrics.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Icon className={`h-4 w-4 ${item.color}`} />
                    <span className="text-sm text-muted-foreground">{item.label}</span>
                  </div>
                  <span className="font-medium">{item.value}</span>
                </div>
              );
            })}
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader>
            <CardTitle>Additional Metrics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b border-border">
              <span className="text-sm text-muted-foreground">Avg. Job Duration</span>
              <Badge variant="outline">Coming soon</Badge>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-border">
              <span className="text-sm text-muted-foreground">Revenue (MTD)</span>
              <Badge variant="outline">Coming soon</Badge>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-border">
              <span className="text-sm text-muted-foreground">Active Subscriptions</span>
              <Badge variant="outline">Coming soon</Badge>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-muted-foreground">Churn Rate</span>
              <Badge variant="outline">Coming soon</Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

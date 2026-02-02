import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import { Button } from "@poly/ui/button";
import { Badge } from "@poly/ui/badge";
import { ArrowLeft, Briefcase, Clock, CheckCircle, XCircle, Pause, RefreshCw, AlertTriangle, FileText, Activity, Zap } from "lucide-react";

type JobDetail = {
  id: string;
  filename?: string;
  status: "QUEUED" | "RUNNING" | "SUCCEEDED" | "FAILED" | "CANCELED";
  language?: string | null;
  engine?: string | null;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  team_id?: string;
  team_name?: string;
  progress?: {
    stage?: string;
    percent?: number;
  };
  error_message?: string | null;
  attempts?: number;
  duration_ms?: number;
};

export function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [job, setJob] = useState<JobDetail | null>(null);

  useEffect(() => {
    if (id) {
      apiFetch<JobDetail>(`/admin/jobs/${id}`).then(setJob);
    }
  }, [id]);

  if (!job) {
    return <div className="p-8">Loading...</div>;
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, { variant: any; icon: any; label: string }> = {
      QUEUED: { variant: "secondary", icon: Clock, label: "Queued" },
      RUNNING: { variant: "default", icon: RefreshCw, label: "Running" },
      SUCCEEDED: { variant: "default", icon: CheckCircle, label: "Succeeded" },
      FAILED: { variant: "destructive", icon: XCircle, label: "Failed" },
      CANCELED: { variant: "outline", icon: Pause, label: "Canceled" },
    };
    const config = colors[status] || { variant: "outline", icon: Clock, label: status };
    const Icon = config.icon;
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {config.label}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/jobs")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight mb-2">Job Details</h1>
          <p className="text-muted-foreground">Job ID: {job.id}</p>
        </div>
        {getStatusBadge(job.status)}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Briefcase className="h-5 w-5" />
              Job Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Filename</div>
                <div className="font-medium">{job.filename || "-"}</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Activity className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Status</div>
                {getStatusBadge(job.status)}
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Zap className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Engine</div>
                <Badge variant="outline">{job.engine || "-"}</Badge>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Language</div>
                <div className="font-medium">{job.language || "-"}</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Briefcase className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Team</div>
                <div className="font-medium">{job.team_name || "-"}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Timeline
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <Clock className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Created At</div>
                <div className="font-medium">{new Date(job.created_at).toLocaleString()}</div>
              </div>
            </div>
            {job.started_at && (
              <div className="flex items-start gap-3">
                <Activity className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm text-muted-foreground">Started At</div>
                  <div className="font-medium">{new Date(job.started_at).toLocaleString()}</div>
                </div>
              </div>
            )}
            {job.completed_at && (
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm text-muted-foreground">Completed At</div>
                  <div className="font-medium">{new Date(job.completed_at).toLocaleString()}</div>
                </div>
              </div>
            )}
            {job.duration_ms && (
              <div className="flex items-start gap-3">
                <Clock className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm text-muted-foreground">Duration</div>
                  <div className="font-medium">{(job.duration_ms / 1000).toFixed(2)}s</div>
                </div>
              </div>
            )}
            {job.attempts !== undefined && (
              <div className="flex items-start gap-3">
                <RefreshCw className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm text-muted-foreground">Attempts</div>
                  <div className="font-medium">{job.attempts}</div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {job.progress && (
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Progress
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Stage</span>
                <span className="text-sm font-medium">{job.progress.stage || "-"}</span>
              </div>
              {job.progress.percent !== undefined && (
                <>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Progress</span>
                    <span className="text-sm font-medium">{job.progress.percent}%</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all"
                      style={{ width: `${job.progress.percent}%` }}
                    />
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {job.error_message && (
        <Card className="border-destructive/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              Error Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 font-mono text-sm">
              {job.error_message}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex items-center gap-4">
        {(job.status === "FAILED" || job.status === "CANCELED") && (
          <Button
            onClick={() => {
              apiFetch(`/admin/jobs/${job.id}/retry`, { method: "POST" }).then(() => {
                window.alert("Job queued for retry");
                navigate("/jobs");
              });
            }}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry Job
          </Button>
        )}
        {(job.status === "QUEUED" || job.status === "RUNNING") && (
          <Button
            variant="destructive"
            onClick={() => {
              if (window.confirm("Are you sure you want to cancel this job?")) {
                apiFetch(`/admin/jobs/${job.id}/cancel`, { method: "POST" }).then(() => {
                  window.alert("Job canceled");
                  navigate("/jobs");
                });
              }
            }}
          >
            <Pause className="h-4 w-4 mr-2" />
            Cancel Job
          </Button>
        )}
        <Button variant="outline" onClick={() => navigate("/jobs")}>
          Back to Jobs
        </Button>
      </div>
    </div>
  );
}

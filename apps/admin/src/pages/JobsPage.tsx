import { ConfirmDialog } from "@poly/ui";
import { Badge } from "@poly/ui/badge";
import { Button } from "@poly/ui/button";
import { Card, CardContent } from "@poly/ui/card";
import { Input } from "@poly/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@poly/ui/table";
import type { LucideIcon } from "lucide-react";
import {
  Briefcase,
  CheckCircle,
  Clock,
  Filter,
  Pause,
  RefreshCw,
  Search,
  XCircle,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";

type JobItem = {
  id: string;
  filename?: string;
  status: "QUEUED" | "RUNNING" | "SUCCEEDED" | "FAILED" | "CANCELED";
  language?: string | null;
  engine?: string | null;
  created_at: string;
  team_name?: string;
};

type BadgeVariant = "default" | "secondary" | "destructive" | "outline";
type StatusFilter = "all" | "QUEUED" | "RUNNING" | "SUCCEEDED" | "FAILED" | "CANCELED";
type EngineFilter = "all" | "whisper" | "speechmatics" | "assemblyai";

export function JobsPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<JobItem[]>([]);
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [engineFilter, setEngineFilter] = useState<EngineFilter>("all");
  const [jobToCancel, setJobToCancel] = useState<string | null>(null);

  const refresh = useCallback(() => {
    const q = query.trim();
    const queryString = q ? `?q=${encodeURIComponent(q)}` : "";
    apiFetch<{ items: JobItem[] }>(`/admin/jobs${queryString}`).then((data) =>
      setItems(data.items),
    );
  }, [query]);

  useEffect(() => {
    const handle = setTimeout(() => {
      refresh();
    }, 300);
    return () => clearTimeout(handle);
  }, [refresh]);

  const filteredItems = items.filter((job) => {
    const statusMatch = statusFilter === "all" || job.status === statusFilter;
    const engineMatch = engineFilter === "all" || job.engine === engineFilter;
    return statusMatch && engineMatch;
  });

  const confirmCancelJob = async () => {
    if (!jobToCancel) return;
    await apiFetch(`/admin/jobs/${jobToCancel}/cancel`, { method: "POST" });
    setJobToCancel(null);
    refresh();
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, { variant: BadgeVariant; icon: LucideIcon }> = {
      QUEUED: { variant: "secondary", icon: Clock },
      RUNNING: { variant: "default", icon: RefreshCw },
      SUCCEEDED: { variant: "default", icon: CheckCircle },
      FAILED: { variant: "destructive", icon: XCircle },
      CANCELED: { variant: "outline", icon: Pause },
    };
    const config = colors[status] || { variant: "outline", icon: Clock };
    const Icon = config.icon;
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {status}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Jobs</h1>
        <p className="text-muted-foreground">Monitor and manage transcription jobs.</p>
      </div>

      <Card className="border-border">
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by filename"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              <Filter className="h-4 w-4 text-muted-foreground mt-2" />
              {(["all", "QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELED"] as const).map(
                (f) => (
                  <Button
                    key={f}
                    variant={statusFilter === f ? "default" : "outline"}
                    size="sm"
                    className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                    onClick={() => setStatusFilter(f)}
                  >
                    {f === "all" ? "All Status" : f}
                  </Button>
                ),
              )}
              {(["all", "whisper", "speechmatics", "assemblyai"] as const).map((f) => (
                <Button
                  key={f}
                  variant={engineFilter === f ? "default" : "outline"}
                  size="sm"
                  className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                  onClick={() => setEngineFilter(f)}
                >
                  {f === "all" ? "All Engines" : f}
                </Button>
              ))}
              <Button
                variant="outline"
                size="sm"
                className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                onClick={refresh}
              >
                Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Job ID</TableHead>
              <TableHead>Filename</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Language</TableHead>
              <TableHead>Engine</TableHead>
              <TableHead>Team</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredItems.map((job) => (
              <TableRow key={job.id}>
                <TableCell>
                  <span className="font-mono text-xs">{job.id.slice(0, 8)}</span>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Briefcase className="h-4 w-4 text-muted-foreground" />
                    <span>{job.filename || "-"}</span>
                  </div>
                </TableCell>
                <TableCell>{getStatusBadge(job.status)}</TableCell>
                <TableCell>{job.language || "-"}</TableCell>
                <TableCell>
                  <Badge variant="outline">{job.engine || "-"}</Badge>
                </TableCell>
                <TableCell>{job.team_name || "-"}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span>{new Date(job.created_at).toLocaleDateString()}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                      onClick={() => navigate(`/jobs/${job.id}`)}
                    >
                      View
                    </Button>
                    {(job.status === "FAILED" || job.status === "CANCELED") && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                        onClick={() =>
                          apiFetch(`/admin/jobs/${job.id}/retry`, {
                            method: "POST",
                          }).then(refresh)
                        }
                      >
                        Retry
                      </Button>
                    )}
                    {(job.status === "QUEUED" || job.status === "RUNNING") && (
                      <Button
                        variant="destructive"
                        size="sm"
                        className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                        onClick={() => setJobToCancel(job.id)}
                      >
                        Cancel
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
            {!filteredItems.length && (
              <TableRow>
                <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                  No jobs found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>

      <ConfirmDialog
        open={!!jobToCancel}
        onOpenChange={(open) => !open && setJobToCancel(null)}
        title="Cancel Job"
        description="Are you sure you want to cancel this job? This action cannot be undone."
        onConfirm={confirmCancelJob}
        confirmText="Cancel Job"
        variant="destructive"
      />
    </div>
  );
}

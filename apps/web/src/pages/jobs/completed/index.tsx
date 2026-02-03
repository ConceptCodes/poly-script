import { Button } from "@poly/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@poly/ui/select";
import { useQuery } from "@tanstack/react-query";
import { Filter } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../../lib/api";
import { JobListSkeleton } from "../pending/components/JobListSkeleton";
import { CompletedJobCard } from "./components/cards/CompletedJobCard";

export function CompletedJobsPage() {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const {
    data: jobsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["completed-jobs", statusFilter],
    queryFn: () => api.getCompletedJobs({ status: statusFilter === "all" ? undefined : statusFilter }),
  });

  const jobs = jobsData?.jobs || [];

  const handleViewJob = (jobId: string) => {
    navigate(`/transcripts/${jobId}`);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card>
          <CardHeader>
            <CardTitle>Completed Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <JobListSkeleton />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card className="border-destructive">
          <CardContent className="p-6">
            <p className="text-destructive">
              {error instanceof Error ? error.message : "An error occurred loading jobs"}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>Completed Jobs</CardTitle>
          <Button variant="ghost" size="sm" onClick={() => navigate("/upload")}>
            Upload Audio
          </Button>
        </CardHeader>
        <CardContent>
          <div className="mb-6 flex items-center gap-4">
            <Filter className="w-4 h-4 text-muted-foreground" />
            <div className="flex-1">
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Completed</SelectItem>
                  <SelectItem value="succeeded">Succeeded</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                  <SelectItem value="canceled">Canceled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {jobs.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-4">
                {statusFilter === "all"
                  ? "No completed jobs found"
                  : `No ${statusFilter} jobs found`}
              </p>
              <Button onClick={() => navigate("/upload")}>Upload Audio</Button>
            </div>
          ) : (
            <div className="space-y-4">
              {jobs.map((job) => (
                <CompletedJobCard
                  key={job.id}
                  jobId={job.id}
                  filename={job.filename}
                  status={job.status}
                  language={job.language}
                  createdAt={job.created_at}
                  finishedAt={job.finished_at}
                  onView={handleViewJob}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

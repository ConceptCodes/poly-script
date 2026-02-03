import { Button, ConfirmDialog } from "@poly/ui";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, RefreshCw } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../../lib/api";
import { PendingJobCard } from "./components/cards/PendingJobCard";
import { JobListSkeleton } from "./components/JobListSkeleton";

export function PendingJobsPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [jobToDelete, setJobToDelete] = useState<string | null>(null);

  const {
    data: jobsData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["pending-jobs"],
    queryFn: () => api.getPendingJobs(),
    refetchInterval: 3000,
  });

  const cancelJobMutation = useMutation({
    mutationFn: (jobId: string) => api.cancelJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pending-jobs"] });
    },
  });

  const handleViewJob = (jobId: string) => {
    navigate(`/jobs/${jobId}/live`);
  };

  const handleCancelJob = (jobId: string) => {
    setJobToDelete(jobId);
  };

  const confirmCancel = () => {
    if (jobToDelete) {
      cancelJobMutation.mutate(jobToDelete);
      setJobToDelete(null);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card>
          <CardHeader>
            <CardTitle>Pending Jobs</CardTitle>
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
            <div className="flex items-center gap-3 text-destructive">
              <AlertCircle className="w-6 h-6" />
              <div>
                <h3 className="font-semibold text-lg mb-1">Error Loading Jobs</h3>
                <p className="text-sm text-muted-foreground">
                  {error instanceof Error ? error.message : "An unknown error occurred"}
                </p>
              </div>
            </div>
            <Button variant="outline" className="flex items-center gap-2" onClick={() => refetch()}>
              <RefreshCw className="w-4 h-4" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const jobs = jobsData?.jobs || [];

  return (
    <div className="container mx-auto py-8 px-4">
      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>Pending Jobs</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            className="flex items-center gap-2"
            onClick={() => refetch()}
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
        </CardHeader>
        <CardContent>
          {jobs.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-4">No pending jobs</p>
              <Button onClick={() => navigate("/upload")}>Upload Audio</Button>
            </div>
          ) : (
            <div className="space-y-4">
              {jobs.map((job) => (
                <PendingJobCard
                  key={job.id}
                  jobId={job.id}
                  filename={job.filename}
                  status={job.status}
                  progressPct={job.progress_pct}
                  progressStage={job.progress_stage}
                  language={job.language}
                  createdAt={job.created_at}
                  onView={handleViewJob}
                  onCancel={handleCancelJob}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
      <ConfirmDialog
        open={!!jobToDelete}
        onOpenChange={(open) => !open && setJobToDelete(null)}
        title="Cancel Job"
        description="Are you sure you want to cancel this job? This action cannot be undone."
        onConfirm={confirmCancel}
        confirmText="Cancel Job"
        variant="destructive"
      />
    </div>
  );
}

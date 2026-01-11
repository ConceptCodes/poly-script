import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@poly-ui/button";
import { AlertCircle, CheckCircle2, ArrowLeft } from "lucide-react";

import { ProgressCard } from "./components/cards/ProgressCard";
import { LiveTranscriptArea } from "./components/LiveTranscriptArea";
import { api } from "../../../lib/api";

interface ProgressData {
  job_id: string;
  status: string;
  progress_pct: number;
  progress_stage: string | null;
  timestamp: string;
}

interface Segment {
  id: number;
  start_ms: number;
  end_ms: number;
  text: string;
  speaker: string | null;
}

export function LiveTranscriptViewerPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();

  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [segments, setSegments] = useState<Segment[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState(false);

  const { data: jobDetail, isLoading } = useQuery({
    queryKey: ["job-detail", jobId],
    queryFn: () => api.getJobDetail(jobId!),
    enabled: !!jobId,
  });

  useEffect(() => {
    if (!jobId) return;

    const eventSource = new EventSource(
      `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/v1/jobs/${jobId}/live`
    );

    eventSource.onmessage = (event) => {
      try {
        const data: ProgressData = JSON.parse(event.data);
        setProgress(data);

        if (data.status === "SUCCEEDED") {
          setIsComplete(true);
          setTimeout(() => {
            navigate(`/transcripts/${jobId}`);
          }, 3000);
        }

        if (data.status === "FAILED" || data.status === "CANCELED") {
          setIsComplete(true);
        }
      } catch (err) {
        console.error("Error parsing SSE message:", err);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE error:", err);
      setError("Connection to job progress failed");
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [jobId, navigate]);

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-muted rounded-lg" />
          <div className="h-96 bg-muted rounded-lg" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center gap-3 text-destructive">
          <AlertCircle className="w-6 h-6" />
          <div>
            <h3 className="font-semibold text-lg mb-1">Connection Error</h3>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!jobDetail && !error) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center gap-3 text-muted-foreground">
          <AlertCircle className="w-6 h-6" />
          <div>
            <h3 className="font-semibold text-lg mb-1">Job Not Found</h3>
            <p className="text-sm">The requested job could not be found.</p>
          </div>
        </div>
      </div>
    );
  }

  const currentProgress = progress || {
    job_id: jobId!,
    status: jobDetail!.status,
    progress_pct: jobDetail!.progress_pct,
    progress_stage: jobDetail!.progress_stage,
    timestamp: new Date().toISOString(),
  };

  const isFinished = isComplete || ["SUCCEEDED", "FAILED", "CANCELED"].includes(currentProgress.status);

  return (
    <div className="container mx-auto py-8 px-4">
      <Button
        variant="ghost"
        className="mb-6 flex items-center gap-2"
        onClick={() => navigate("/jobs/pending")}
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Jobs
      </Button>

      <div className="space-y-6">
        <ProgressCard
          filename={jobDetail!.filename}
          status={currentProgress.status}
          progressPct={currentProgress.progress_pct}
          progressStage={currentProgress.progress_stage}
          language={jobDetail!.requested_language}
          createdAt={jobDetail!.created_at}
          audioDuration={jobDetail!.audio_duration_seconds}
        />

        {isFinished && currentProgress.status === "SUCCEEDED" && (
          <div className="flex items-center justify-center gap-3 p-4 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
            <CheckCircle2 className="w-8 h-8 text-green-600 dark:text-green-400" />
            <div>
              <h3 className="font-semibold text-lg text-green-900 dark:text-green-100">
                Transcription Complete
              </h3>
              <p className="text-sm text-green-700 dark:text-green-300">
                Redirecting to transcript editor...
              </p>
            </div>
          </div>
        )}

        {isFinished && currentProgress.status === "FAILED" && (
          <div className="flex items-center gap-3 p-4 bg-red-50 dark:bg-red-950 rounded-lg border border-red-200 dark:border-red-800">
            <AlertCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
            <div>
              <h3 className="font-semibold text-lg text-red-900 dark:text-red-100">
                Transcription Failed
              </h3>
              <p className="text-sm text-red-700 dark:text-red-300">
                The transcription encountered an error. Please try again.
              </p>
            </div>
          </div>
        )}

        {isFinished && currentProgress.status === "CANCELED" && (
          <div className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-950 rounded-lg border border-gray-200 dark:border-gray-800">
            <CheckCircle2 className="w-8 h-8 text-gray-600 dark:text-gray-400" />
            <div>
              <h3 className="font-semibold text-lg text-gray-900 dark:text-gray-100">
                Job Canceled
              </h3>
              <p className="text-sm text-gray-700 dark:text-gray-300">
                This job was canceled.
              </p>
            </div>
          </div>
        )}

        {!isFinished && (
          <LiveTranscriptArea
            segments={segments}
            isComplete={isComplete}
          />
        )}
      </div>
    </div>
  );
}

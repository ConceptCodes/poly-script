import { Badge } from "@poly/ui/badge";
import { Button } from "@poly/ui/button";
import { Card, CardContent } from "@poly/ui/card";
import { Progress } from "@poly/ui/progress";
import { formatDistanceToNow } from "date-fns";
import { Clock, FileText, Play } from "lucide-react";

interface PendingJobCardProps {
  jobId: string;
  filename: string;
  status: string;
  progressPct: number;
  progressStage: string | null;
  language: string | null;
  createdAt: string;
  onView: (jobId: string) => void;
  onCancel: (jobId: string) => void;
}

export function PendingJobCard({
  jobId,
  filename,
  status,
  progressPct,
  progressStage,
  language,
  createdAt,
  onView,
  onCancel,
}: PendingJobCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "QUEUED":
        return "bg-yellow-500";
      case "RUNNING":
        return "bg-blue-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <FileText className="w-5 h-5 text-muted-foreground" aria-hidden="true" />
              <h3 className="font-semibold text-lg">{filename}</h3>
              <Badge className={getStatusColor(status)}>{status}</Badge>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              {language && (
                <span className="flex items-center gap-1">
                  <span className="font-medium">Language:</span>
                  <span>{language.toUpperCase()}</span>
                </span>
              )}
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" aria-hidden="true" />
                {formatDistanceToNow(new Date(createdAt), { addSuffix: true })}
              </span>
            </div>
          </div>
        </div>

        {status === "RUNNING" && (
          <div className="mb-4">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-muted-foreground">{progressStage || "Processing"}</span>
              <span className="font-medium">{progressPct}%</span>
            </div>
            <Progress value={progressPct} className="w-full" />
          </div>
        )}

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            className="flex items-center gap-2"
            onClick={() => onView(jobId)}
          >
            <Play className="w-4 h-4" aria-hidden="true" />
            View Progress
          </Button>
          {status === "QUEUED" && (
            <Button variant="destructive" size="sm" onClick={() => onCancel(jobId)}>
              Cancel
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

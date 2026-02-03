import { Badge } from "@poly/ui/badge";
import { Button } from "@poly/ui/button";
import { Card, CardContent } from "@poly/ui/card";
import { formatDistanceToNow } from "date-fns";
import { AlertCircle, CheckCircle2, Clock, FileText, XCircle } from "lucide-react";

interface CompletedJobCardProps {
  jobId: string;
  filename: string;
  status: string;
  language: string | null;
  finishedAt: string | null;
  onView: (jobId: string) => void;
}

export function CompletedJobCard({
  jobId,
  filename,
  status,
  language,
  finishedAt,
  onView,
}: CompletedJobCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "SUCCEEDED":
        return "bg-green-500";
      case "FAILED":
        return "bg-red-500";
      case "CANCELED":
        return "bg-gray-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "SUCCEEDED":
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case "FAILED":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "CANCELED":
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "SUCCEEDED":
        return "Completed";
      case "FAILED":
        return "Failed";
      case "CANCELED":
        return "Canceled";
      default:
        return status;
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <FileText className="w-5 h-5 text-muted-foreground" />
              <h3 className="font-semibold text-lg">{filename}</h3>
              <Badge className={getStatusColor(status)}>{getStatusText(status)}</Badge>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              {language && (
                <span className="flex items-center gap-1">
                  <span className="font-medium">Language:</span>
                  <span>{language.toUpperCase()}</span>
                </span>
              )}
              {finishedAt && (
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {formatDistanceToNow(new Date(finishedAt), { addSuffix: true })}
                </span>
              )}
            </div>
          </div>
          <div className="ml-4">{getStatusIcon(status)}</div>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            className="flex items-center gap-2"
            onClick={() => onView(jobId)}
          >
            <FileText className="w-4 h-4" />
            View Result
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
